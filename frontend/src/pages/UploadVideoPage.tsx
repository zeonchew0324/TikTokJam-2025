import { useRef, useState } from 'react'
import '../stylesheets/UploadVideoPage.css'

export type UploadedVideo = {
  id: string;
  url: string;
  title: string;
  description: string;
  creator: string;
  hashtags: string[];
}

export function UploadVideoPage(props: { onUploaded?: (video: UploadedVideo) => void }) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [videoSelected, setVideoSelected] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [hashtags, setHashtags] = useState('')

  function handlePick() {
    inputRef.current?.click()
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null
    setFile(f)
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(f ? URL.createObjectURL(f) : null)
    setVideoSelected(true)
  }

  function handleRemove() {
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(null)
    setFile(null)
    setVideoSelected(false)
    setTitle('')
    setDescription('')
    setHashtags('')
    if (inputRef.current) inputRef.current.value = ''
  }

  async function handleUpload() {
    if (!file || !title.trim() || !description.trim()) {
      alert('Please fill in title and description fields');
      return;
    }
    
    setIsUploading(true)
    try {
      const form = new FormData()
      form.append('video', file)
      // TODO: point to your real backend endpoint
      // Example: const res = await fetch('/api/upload', { method: 'POST', body: form })
      await new Promise(r => setTimeout(r, 800))
      console.log('Simulated upload complete:', file.name)
      const localUrl = previewUrl ?? URL.createObjectURL(file)
      
      // Create video object with metadata
      const videoObject: UploadedVideo = {
        id: Date.now().toString(), // Simple ID generation
        url: localUrl,
        title: title.trim(),
        description: description.trim(),
        hashtags: hashtags.split(' ').filter(tag => tag.startsWith('#')).map(tag => tag.slice(1))
      }
      
      props.onUploaded?.(videoObject)
    } catch (err) {
      console.error(err)
      alert('Upload failed')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div>
      <h2>Upload Video</h2>

      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      <div style={{ display: 'flex', gap: 8 }}>
        <button className="upload-button" onClick={handlePick}>Choose File</button>
        {videoSelected && (
            <button
            className="upload-button"
            onClick={handleUpload}
            disabled={!file || isUploading || !title.trim() || !description.trim()}
            >
            {isUploading ? 'Uploading…' : 'Upload'}
            </button>
        )}
      </div>

      {/* Video metadata input fields */}
      {videoSelected && (
        <div className="video-metadata" style={{ marginTop: 16, maxWidth: 480 }}>
          <div style={{ marginBottom: 12 }}>
            <label htmlFor="video-title" style={{ display: 'block', marginBottom: 4, color: 'white', fontWeight: 600 }}>
              Video Title *
            </label>
            <input
              id="video-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter video title..."
              className="metadata-input"
              style={{ width: '100%' }}
            />
          </div>
          
          <div style={{ marginBottom: 12 }}>
            <label htmlFor="video-description" style={{ display: 'block', marginBottom: 4, color: 'white', fontWeight: 600 }}>
              Video Description *
            </label>
            <textarea
              id="video-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter video description..."
              className="metadata-input"
              rows={3}
              style={{ width: '100%', resize: 'vertical' }}
            />
          </div>
          
          <div style={{ marginBottom: 12 }}>
            <label htmlFor="video-hashtags" style={{ display: 'block', marginBottom: 4, color: 'white', fontWeight: 600 }}>
              Hashtags
            </label>
            <input
              id="video-hashtags"
              type="text"
              value={hashtags}
              onChange={(e) => setHashtags(e.target.value)}
              placeholder="Enter hashtags (e.g., #funny #viral #trending)"
              className="metadata-input"
              style={{ width: '100%' }}
            />
          </div>
        </div>
      )}

      {file && (
        <div style={{ marginTop: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <span>Selected: {file.name}</span>
            <button
              className="remove-button"
              onClick={handleRemove}
              title="Remove video"
            >
              <span className="material-symbols-outlined">delete</span>
            </button>
          </div>
          {previewUrl && (
            <video src={previewUrl} controls style={{ maxWidth: 480, width: '100%', marginTop: 8 }} />
          )}
        </div>
      )}
    </div>
  )
}