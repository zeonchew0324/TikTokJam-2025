import { useRef, useState } from 'react'
import '../stylesheets/UploadVideoPage.css'

export type UploadedVideo = {
  id: string;
  url: string;
  title: string; // Keep for compatibility
  description: string;
  creator: string; // Keep for compatibility
  hashtags: string[]; // Keep for compatibility
}

export function UploadVideoPage(props: { onUploaded?: (video: UploadedVideo) => void }) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [videoSelected, setVideoSelected] = useState(false)
  const [description, setDescription] = useState('')

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
    setDescription('')
    if (inputRef.current) inputRef.current.value = ''
  }

  async function handleUpload() {
    if (!file || !description.trim()) {
      alert('Please enter a video description');
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
        title: file.name.split('.')[0], // Use filename as title
        description: description.trim(),
        creator: "User", // Default creator
        hashtags: [] // Empty hashtags
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
            disabled={!file || isUploading || !description.trim()}
            >
            {isUploading ? 'Uploading…' : 'Upload'}
            </button>
        )}
      </div>

      {/* Video metadata input fields - Only Description */}
      {videoSelected && (
        <div className="video-metadata" style={{ marginTop: 16, maxWidth: 480 }}>
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