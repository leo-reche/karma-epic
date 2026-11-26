export default function ResultCard({ file, progress, markdown }) {
  const fileName = file && `${file.name.replace(/\.[^.]+$/, '')}.md`

  const download = () => {
    const url = URL.createObjectURL(new Blob([markdown], { type: 'text/markdown' }))
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  return (
    <section className="card">
      <h2>Download the result</h2>
      <div className="result">
        {!file && <span className="hint">Your file will appear here</span>}
        {file && !markdown && (
          <div className="progress">
            <progress max="100" value={progress} aria-label="Processing video" />
            <div className="hint">
              <span>Processing your video</span>
              <span>{progress}%</span>
            </div>
          </div>
        )}
        {markdown && <span role="status">{fileName} is ready</span>}
        <button type="button" className="download" disabled={!markdown} onClick={download}>
          Download .md
        </button>
        <span className="hint">Then give it to your favourite LLM.</span>
      </div>
    </section>
  )
}
