import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0]
      if (selected.type !== 'audio/mpeg') {
        setMessage('Please select a valid MP3 file.')
        return
      }
      setFile(selected)
      setMessage('')
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setMessage('No file selected.')
      return
    }
    const formData = new FormData()
    formData.append('file', file)
    try {
      setUploading(true)
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData,
      })
      if (response.ok) {
        setMessage('File uploaded successfully!')
      } else {
        setMessage('Upload failed.')
      }
    } catch (error) {
      console.error(error)
      setMessage('An error occurred while uploading.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <>
      <div className="card">
        <form onSubmit={handleUpload}>
          <input type="file" accept="audio/mpeg" onChange={handleFileChange} />
          <button type="submit" disabled={uploading}>
            {uploading ? 'Uploading...' : 'Upload MP3'}
          </button>
        </form>
        {message && <p>{message}</p>}
      </div>
    </>
  )
}

export default App
