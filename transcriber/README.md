# Karma-LLMifier script

`transcribe.py` turns one video into a Markdown file you can give to an AI. It creates a timestamped transcript and saves up to 20 screenshots, mostly chosen where on-screen content changes. It runs on your computer. Slide text is only in the images, and speakers are not labelled.

## Setup (once, from the project folder, in PowerShell)

```powershell
python -m venv transcriber\.venv
.\transcriber\.venv\Scripts\python -m pip install -r transcriber\requirements.txt
```

## Use

Put videos in `inputs\`, then run:

```powershell
.\transcriber\.venv\Scripts\python transcriber\transcribe.py "inputs\my video.mp4"
```

Results appear in `output\my video\`. Running again overwrites them. The first run downloads the speech model.

| Option | Purpose | Default |
| --- | --- | --- |
| `--model` | `tiny` is faster, less accurate | `large-v3-turbo` |
| `--language` | For example `en`, `es`, `pt` | auto |
| `--screenshots` | Maximum number, `0` for none | `20` |
| `--output` | Results folder | `output` beside the video's folder |
