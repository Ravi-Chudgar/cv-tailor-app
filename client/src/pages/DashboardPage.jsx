import React, { useState, useEffect } from 'react'
import CVUploader from '../components/CVUploader'
import JobDescriptionForm from '../components/JobDescriptionForm'
import TailoringResults from '../components/TailoringResults'
import { tailorAPI, cvAPI } from '../api/client'
import { useCVStore } from '../stores/cvStore'
import { Loader, AlertCircle, Upload, FileText, Briefcase, Sparkles, Phone, MapPin, ArrowLeft } from 'lucide-react'

export default function DashboardPage() {
  const [selectedCVFile, setSelectedCVFile] = useState('')
  const [tailoringResult, setTailoringResult] = useState(null)
  const [isTailoring, setIsTailoring] = useState(false)
  const [error, setError] = useState('')
  const [isLoadingCVs, setIsLoadingCVs] = useState(true)
  const [mobileNumber, setMobileNumber] = useState('')
  const [location, setLocation] = useState('')
  const { cvs, setCVs, jobDescription } = useCVStore()

  useEffect(() => {
    const loadCVs = async () => {
      try {
        setIsLoadingCVs(true)
        console.log('Loading CVs...')
        
        // Set a timeout for the API call (5 seconds)
        const timeoutPromise = new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Request timeout')), 5000)
        )
        
        const response = await Promise.race([
          cvAPI.list(),
          timeoutPromise
        ])
        
        console.log('CVs loaded:', response.data)
        setCVs(response.data.cvs || [])
      } catch (err) {
        console.error('Failed to load CVs:', err.message)
        // Set empty array on error instead of causing issues
        setCVs([])
      } finally {
        setIsLoadingCVs(false)
      }
    }
    
    loadCVs()
  }, [setCVs])

  const handleTailorCV = async () => {
    if (!selectedCVFile) {
      setError('Please select a CV file')
      return
    }

    if (!jobDescription) {
      setError('Please analyze a job description first')
      return
    }

    setIsTailoring(true)
    setError('')

    try {
      const response = await tailorAPI.tailor(selectedCVFile, jobDescription, mobileNumber, location)
      setTailoringResult(response.data)
    } catch (err) {
      console.error('[TAILOR] Error:', err.response?.data || err.message)
      const detail = err.response?.data?.detail
      let errorMessage = 'Failed to tailor CV'
      
      if (Array.isArray(detail)) {
        // Handle validation errors array
        errorMessage = detail.map(d => d.msg || d.toString()).join(', ')
      } else if (typeof detail === 'string') {
        errorMessage = detail
      } else if (err.response?.data) {
        errorMessage = JSON.stringify(err.response.data)
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
    } finally {
      setIsTailoring(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50/30">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

        {/* Hero header */}
        {!tailoringResult && (
          <div className="text-center mb-10 slide-up">
            <h1 className="text-4xl sm:text-5xl font-extrabold bg-gradient-to-r from-indigo-700 via-purple-600 to-indigo-700 bg-clip-text text-transparent mb-3">
              Tailor Your CV
            </h1>
            <p className="text-gray-500 text-lg max-w-xl mx-auto">
              Upload your CV, paste the job description, and get an ATS-optimised resume in seconds.
            </p>
          </div>
        )}

        {error && !tailoringResult && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl flex gap-3 items-start slide-up">
            <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
            <div className="text-sm">{error}</div>
          </div>
        )}

        {!tailoringResult ? (
          <div className="space-y-8">

            {/* Step 1 — Upload */}
            <section className="slide-up" style={{ animationDelay: '0.05s' }}>
              <div className="flex items-center gap-3 mb-4">
                <div className="step-badge bg-indigo-600 text-white">1</div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Upload Your CV</h2>
                  <p className="text-sm text-gray-500">PDF or DOCX, up to 10 MB</p>
                </div>
              </div>
              <CVUploader />
            </section>

            {/* Step 2 — Select CV */}
            <section className="slide-up" style={{ animationDelay: '0.1s' }}>
              <div className="flex items-center gap-3 mb-4">
                <div className="step-badge bg-indigo-600 text-white">2</div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Select CV</h2>
                  <p className="text-sm text-gray-500">Choose the CV you want to tailor</p>
                </div>
              </div>

              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                {isLoadingCVs ? (
                  <div className="flex items-center gap-3 text-gray-500 py-2">
                    <Loader size={18} className="animate-spin" />
                    <span className="text-sm">Loading your CVs...</span>
                  </div>
                ) : cvs && cvs.length > 0 ? (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      <FileText size={14} className="inline mr-1 -mt-0.5" />
                      Your CVs
                    </label>
                    <select
                      value={selectedCVFile}
                      onChange={(e) => setSelectedCVFile(e.target.value)}
                      className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                    >
                      <option value="">Choose a CV file...</option>
                      {cvs.map((cv) => (
                        <option key={cv.file_id} value={cv.file_id}>
                          {cv.file_name}
                        </option>
                      ))}
                    </select>
                  </div>
                ) : (
                  <div className="flex items-center gap-3 py-4 px-4 bg-indigo-50 rounded-xl">
                    <Upload size={20} className="text-indigo-500" />
                    <div>
                      <p className="text-sm font-semibold text-indigo-900">No CVs uploaded yet</p>
                      <p className="text-xs text-indigo-600">Upload a CV in Step 1 to get started</p>
                    </div>
                  </div>
                )}
              </div>
            </section>

            {/* Contact Details */}
            <section className="slide-up" style={{ animationDelay: '0.15s' }}>
              <div className="flex items-center gap-3 mb-4">
                <div className="step-badge bg-gray-200 text-gray-600 text-xs">OPT</div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Contact Details</h2>
                  <p className="text-sm text-gray-500">Override mobile number & location on the final CV</p>
                </div>
              </div>

              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      <Phone size={14} className="inline mr-1 -mt-0.5" />
                      Mobile Number
                    </label>
                    <input
                      type="tel"
                      value={mobileNumber}
                      onChange={(e) => setMobileNumber(e.target.value)}
                      placeholder="e.g. +44 7774466825"
                      className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      <MapPin size={14} className="inline mr-1 -mt-0.5" />
                      Location
                    </label>
                    <input
                      type="text"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      placeholder="e.g. London, UK"
                      className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                    />
                  </div>
                </div>
              </div>
            </section>

            {/* Step 3 — Job Description */}
            <section className="slide-up" style={{ animationDelay: '0.2s' }}>
              <div className="flex items-center gap-3 mb-4">
                <div className="step-badge bg-indigo-600 text-white">3</div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Analyze Job Description</h2>
                  <p className="text-sm text-gray-500">Paste the JD to extract keywords & run gap analysis</p>
                </div>
              </div>
              <JobDescriptionForm selectedCVFile={selectedCVFile} />
            </section>

            {/* Tailor Button */}
            {selectedCVFile && jobDescription && (
              <section className="slide-up" style={{ animationDelay: '0.25s' }}>
                <button
                  onClick={handleTailorCV}
                  disabled={isTailoring}
                  className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-2xl font-bold text-lg hover:shadow-xl hover:shadow-indigo-200 disabled:opacity-50 transition-all flex items-center justify-center gap-3"
                >
                  {isTailoring ? (
                    <>
                      <Loader size={22} className="animate-spin" />
                      Tailoring your CV...
                    </>
                  ) : (
                    <>
                      <Sparkles size={22} />
                      Tailor My CV
                    </>
                  )}
                </button>
              </section>
            )}
          </div>
        ) : (
          <div className="slide-up">
            <button
              onClick={() => { setTailoringResult(null); setError('') }}
              className="mb-8 flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
            >
              <ArrowLeft size={16} />
              Start Over
            </button>
            <TailoringResults result={tailoringResult} cvFileName={selectedCVFile} />
          </div>
        )}
      </div>
    </div>
  )
}
