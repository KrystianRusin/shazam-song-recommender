import { useState, useEffect } from 'react'
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
      const response = await fetch('http://localhost:8000/songs/upload', {
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

  useEffect(() => {
    const fetchAndPostSong = async () => {
      try {
        const getRootResponse = await fetch("http://localhost:8000/")
        console.log(getRootResponse)
        // GET request for song with id 1
        const getResponse = await fetch('http://localhost:8000/songs/1')
        if (!getResponse.ok) {
          console.error('Failed to fetch song 1', await getResponse.text())
          return
        }
        const song = await getResponse.json()
        console.log('Fetched song:', song)

        // POST request to add a new song (song 3)
        const newSong = { id: 3, title: 'Song 3', artist: 'Artist 3' }
        const postResponse = await fetch('http://localhost:8000/songs', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newSong),
        })
        if (!postResponse.ok) {
          console.error('Failed to add new song', await postResponse.text())
          return
        }
        const addedSong = await postResponse.json()
        console.log('Added song:', addedSong)
      } catch (error) {
        console.error('Error:', error)
      }
    }
    fetchAndPostSong()
  }, [])

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
