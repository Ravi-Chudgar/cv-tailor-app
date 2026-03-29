import React, { useRef, useState } from 'react'
import { Upload, File, Loader } from 'lucide-react'
import { cvAPI } from '../api/client'
import { useCVStore } from '../stores/cvStore'

export default function CVUploader() {
  const fileInputRef = useRef(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const { setCVs } = useCVStore()

  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file extension (more reliable than mime type)
    const validExtensions = ['.pdf', '.docx', '.doc']
    const fileExtensionMatch = file.name.match(/\.[^.]+$/)
    const fileExtension = fileExtensionMatch ? fileExtensionMatch[0].toLowerCase() : ''
    
    if (!validExtensions.includes(fileExtension)) {
      setError(`Please upload a PDF or DOCX file. You selected: ${fileExtension || 'unknown'}`)
      return
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    setIsLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await cvAPI.upload(file)
      setSuccess(`CV "${file.name}" uploaded successfully!`)
      
      // Fetch updated CV list
      const cvList = await cvAPI.list()
      setCVs(cvList.data.cvs || [])

      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err) {
      console.error('[CVUploader] Upload failed:', err)
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to upload CV'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl border-2 border-dashed border-indigo-200 p-8 text-center hover:border-indigo-400 transition-colors group">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.doc"
        onChange={handleFileSelect}
        disabled={isLoading}
        className="hidden"
      />

      <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-indigo-100 transition-colors">
        <Upload className="text-indigo-600" size={28} />
      </div>

      <h3 className="text-lg font-bold text-gray-900 mb-1">Upload Your CV</h3>
      <p className="text-gray-500 text-sm mb-6">
        Drag and drop or click to select (PDF / DOCX, max 10 MB)
      </p>

      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={isLoading}
        className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium text-sm hover:shadow-lg hover:shadow-indigo-200 disabled:opacity-50 transition-all flex items-center gap-2 mx-auto"
      >
        {isLoading ? (
          <>
            <Loader size={16} className="animate-spin" />
            Uploading...
          </>
        ) : (
          <>
            <File size={16} />
            Choose File
          </>
        )}
      </button>

      {error && (
        <div className="mt-4 p-3.5 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="mt-4 p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl text-sm">
          {success}
        </div>
      )}
    </div>
  )
}
