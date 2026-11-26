"""Turn one video into an LLM-ready Markdown transcript with a few screenshots.

Usage: python transcribe.py path/to/video.mp4
"""

# We will deploy this to Google Cloud projects and users will access it through our published UI.

import argparse
import shutil
import sys
from pathlib import Path

import av
from faster_whisper import WhisperModel
from PIL import ImageChops, ImageFilter, ImageStat

SAMPLE_SECONDS = 5
THUMBNAIL_SIZE = (320, 180)
EDGE_STRENGTH = 40
MIN_DIFFERENCE = 0.35
MIN_BRIGHTNESS = 10
SCREENSHOT_WIDTH = 1280
PARAGRAPH_SECONDS = 30
PARAGRAPH_MAX_SECONDS = 60
PAUSE_SECONDS = 2


def timestamp(seconds, separator=":"):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return separator.join(f"{part:02d}" for part in (hours, minutes, seconds))


def probe(path):
    with av.open(str(path)) as container:
        duration = container.duration / av.time_base if container.duration else 0
        return duration, bool(container.streams.audio), bool(container.streams.video)


def transcribe(path, model_name, language):
    print(f"Loading model '{model_name}' (downloaded on first use)...", flush=True)
    model = WhisperModel(model_name, device="auto", compute_type="int8")
    segments, info = model.transcribe(
        str(path),
        language=language,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    print(f"Transcribing (language: {info.language})...", flush=True)

    results = []
    reported = 0
    for segment in segments:
        results.append(segment)
        percent = min(int(segment.end / info.duration * 100), 100)
        if percent >= reported + 5:
            reported = percent
            print(f"  {percent}% ({timestamp(segment.end)})", flush=True)
    return results, info.language


def sample_frames(path, duration):
    with av.open(str(path)) as container:
        stream = container.streams.video[0]
        start = float((stream.start_time or 0) * stream.time_base)
        seen = set()
        for target in range(0, max(int(duration), 1), SAMPLE_SECONDS):
            container.seek(int((start + target) / stream.time_base), stream=stream)
            for frame in container.decode(stream):
                if frame.time is None or frame.time - start < target - SAMPLE_SECONDS:
                    continue
                if frame.pts not in seen:
                    seen.add(frame.pts)
                    yield max(frame.time - start, 0), frame.to_image()
                break


def edge_mask(image):
    edges = image.convert("L").resize(THUMBNAIL_SIZE).filter(ImageFilter.FIND_EDGES)
    mask = edges.point(lambda value: 255 if value > EDGE_STRENGTH else 0)
    return mask.crop((1, 1, mask.width - 1, mask.height - 1))


def difference(first, second):
    union = ImageStat.Stat(ImageChops.lighter(first, second)).sum[0]
    if not union:
        return 0
    return 1 - ImageStat.Stat(ImageChops.darker(first, second)).sum[0] / union


def pick_screenshots(candidates, limit):
    """Pick the frames whose still text and graphics differ most from each other."""
    if not candidates or limit < 1:
        return []
    first = max(candidates, key=lambda c: ImageStat.Stat(c[1]).sum[0])
    selected = [first]
    distances = [difference(c[1], first[1]) for c in candidates]
    while len(selected) < limit:
        best = max(range(len(candidates)), key=distances.__getitem__)
        if distances[best] < MIN_DIFFERENCE:
            break
        selected.append(candidates[best])
        distances = [
            min(distance, difference(c[1], candidates[best][1]))
            for distance, c in zip(distances, candidates)
        ]
    return sorted(selected, key=lambda c: c[0])


def save_screenshots(path, duration, folder, limit):
    print("Selecting screenshots...", flush=True)
    folder.mkdir(parents=True)
    candidates = []
    previous = None
    for time, image in sample_frames(path, duration):
        if ImageStat.Stat(image.convert("L")).mean[0] < MIN_BRIGHTNESS:
            previous = None
            continue
        mask = edge_mask(image)
        if previous is not None:
            still = ImageChops.darker(mask, previous.filter(ImageFilter.MaxFilter(3)))
            image.thumbnail((SCREENSHOT_WIDTH, SCREENSHOT_WIDTH))
            file = folder / f"{timestamp(time, '-')}.jpg"
            image.save(file, quality=85)
            candidates.append((time, still, file))
        previous = mask

    selected = pick_screenshots(candidates, limit)
    keep = {file for _, _, file in selected}
    for _, _, file in candidates:
        if file not in keep:
            file.unlink(missing_ok=True)
    return [(time, file) for time, _, file in selected]


def paragraphs(segments):
    current = []
    for segment in segments:
        if current:
            length = current[-1].end - current[0].start
            sentence_done = current[-1].text.rstrip().endswith((".", "?", "!"))
            if (
                segment.start - current[-1].end >= PAUSE_SECONDS
                or (length >= PARAGRAPH_SECONDS and sentence_done)
                or length >= PARAGRAPH_MAX_SECONDS
            ):
                yield current[0].start, " ".join(s.text.strip() for s in current)
                current = []
        current.append(segment)
    if current:
        yield current[0].start, " ".join(s.text.strip() for s in current)


def build_markdown(video, duration, language, segments, screenshots):
    entries = [
        (time, 0, f"![Screenshot at {timestamp(time)}](screenshots/{file.name})")
        for time, file in screenshots
    ]
    entries += [
        (start, 1, f"**[{timestamp(start)}]** {text}")
        for start, text in paragraphs(segments)
    ]
    header = [
        "---",
        f'source: "{video.name}"',
        f'duration: "{timestamp(duration)}"',
        f"language: {language}",
        "---",
        "",
        f"# {video.stem}",
        "",
        "Automatic transcript. Timestamps are HH:MM:SS from the start of the video.",
        "",
        "## Transcript",
    ]
    body = [text for _, _, text in sorted(entries)]
    if not segments:
        body.append("_No speech detected._")
    return "\n".join(header) + "\n\n" + "\n\n".join(body) + "\n"


def process_video(video, output_root, model_name="large-v3-turbo", language=None, max_screenshots=20):
    video = Path(video)
    duration, has_audio, has_video = probe(video)
    if not has_audio:
        raise ValueError(f"{video.name} has no audio track")

    output = Path(output_root) / video.stem
    screenshot_folder = output / "screenshots"
    segments, language = transcribe(video, model_name, language)

    shutil.rmtree(screenshot_folder, ignore_errors=True)
    screenshots = []
    if has_video and max_screenshots > 0:
        screenshots = save_screenshots(video, duration, screenshot_folder, max_screenshots)

    output.mkdir(parents=True, exist_ok=True)
    markdown = output / f"{video.stem}.md"
    markdown.write_text(
        build_markdown(video, duration, language, segments, screenshots), encoding="utf-8"
    )
    return markdown


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("video", type=Path)
    parser.add_argument(
        "--output", type=Path, help="default: an 'output' folder next to the video's folder"
    )
    parser.add_argument("--model", default="large-v3-turbo", help="e.g. small, medium, large-v3")
    parser.add_argument("--language", help="e.g. en, es, pt (auto-detected if omitted)")
    parser.add_argument("--screenshots", type=int, default=20, help="maximum number, 0 to disable")
    args = parser.parse_args()

    if not args.video.is_file():
        sys.exit(f"File not found: {args.video}")
    output = args.output or args.video.resolve().parent.parent / "output"
    try:
        markdown = process_video(
            args.video, output, args.model, args.language, args.screenshots
        )
    except (ValueError, av.error.FFmpegError) as error:
        sys.exit(f"Could not process video: {error}")
    print(f"Done: {markdown.resolve()}")


if __name__ == "__main__":
    main()
