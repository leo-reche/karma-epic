// Placeholder until the backend exists: nothing is uploaded and the result is a sample.
export function processVideo(file, { onProgress, signal }) {
  return new Promise((resolve, reject) => {
    let percent = 0
    const timer = setInterval(() => {
      percent = Math.min(100, percent + 2)
      onProgress(percent)
      if (percent === 100) {
        clearInterval(timer)
        resolve(sampleMarkdown(file.name))
      }
    }, 100)
    signal.addEventListener('abort', () => {
      clearInterval(timer)
      reject(signal.reason)
    })
  })
}

function sampleMarkdown(name) {
  return `# ${name.replace(/\.[^.]+$/, '')}

> Sample output. The video was not processed.

## Transcript

**[00:00:00]** Welcome everyone, and thanks for joining today.

**[00:00:12]** We will start with a short overview.

![Screenshot at 00:00:45](screenshots/00-00-45.jpg)

**[00:00:45]** As you can see on this slide, there are three parts.

**[00:01:30]** Let us look at the first one.
`
}
