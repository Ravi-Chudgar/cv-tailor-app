import React, { useState } from 'react'
import { Download, Copy, Eye, X, Loader } from 'lucide-react'
import { pdfAPI } from '../api/client'
import ATSScoreDisplay from './ATSScoreDisplay'

export default function TailoringResults({ result, cvFileName }) {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)
  const [showFullDocument, setShowFullDocument] = useState(false)

  // Extract the user's name from the first non-empty line of the tailored CV
  const getUserFileName = () => {
    if (result?.tailored_cv) {
      const firstLine = result.tailored_cv.split('\n').find(l => l.trim())?.trim()
      if (firstLine) {
        const safeName = firstLine.replace(/[^a-zA-Z\s]/g, '').trim().replace(/\s+/g, '_')
        if (safeName) return `${safeName}_Tailored_CV.pdf`
      }
    }
    return cvFileName || 'tailored_cv.pdf'
  }

  const handleGeneratePDF = async () => {
    setIsGeneratingPDF(true)
    const downloadName = getUserFileName()
    try {
      const response = await pdfAPI.generate(
        result.tailored_cv,
        'professional',
        downloadName
      )
      
      // response.data is already a Blob when responseType: 'blob'
      const url = window.URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', downloadName)
      document.body.appendChild(link)
      link.click()
      window.URL.revokeObjectURL(url)
      link.remove()
    } catch (err) {
      console.error('Failed to generate PDF:', err)
      let errorMsg = err.message
      if (err.response?.data instanceof Blob) {
        try {
          const text = await err.response.data.text()
          const json = JSON.parse(text)
          errorMsg = json.detail || errorMsg
        } catch (_) { /* ignore parse errors */ }
      } else if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail
      }
      alert('Failed to generate PDF: ' + errorMsg)
    } finally {
      setIsGeneratingPDF(false)
    }
  }

  const handleCopyCV = () => {
    navigator.clipboard.writeText(result.tailored_cv)
    setCopySuccess(true)
    setTimeout(() => setCopySuccess(false), 2000)
  }

  return (
    <div className="space-y-6">
      {result.ats_score && <ATSScoreDisplay atsScore={result.ats_score} />}

      {result.ats_details && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8">
          <h3 className="text-lg font-bold mb-5 text-gray-900 flex items-center gap-2">
            <span className="w-7 h-7 bg-emerald-100 rounded-lg flex items-center justify-center text-sm">✅</span>
            ATS Optimization Details
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(result.ats_details).map(([key, value]) => (
              <div key={key} className="bg-gray-50 rounded-xl p-4 border-l-4 border-emerald-400">
                <p className="font-semibold text-gray-800 text-sm capitalize">{key.replace(/_/g, ' ')}</p>
                <p className="text-sm text-gray-500 mt-1">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.ats_improvements && result.ats_improvements.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center gap-2">
            <span className="w-7 h-7 bg-indigo-100 rounded-lg flex items-center justify-center text-sm">🚀</span>
            ATS Improvements Applied
          </h3>
          <div className="space-y-2.5">
            {result.ats_improvements.map((improvement, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 bg-indigo-50/50 rounded-xl">
                <span className="text-indigo-600 font-bold flex-shrink-0 mt-0.5 text-sm">✓</span>
                <p className="text-gray-700 text-sm">{improvement}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.matching_keywords && result.missing_keywords && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8">
          <h3 className="text-lg font-bold mb-5 text-gray-900">Keyword Analysis</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-3 text-emerald-700 text-sm flex items-center gap-1.5">
                <span className="w-5 h-5 bg-emerald-100 rounded-md flex items-center justify-center text-xs">✓</span>
                Matching Keywords
              </h4>
              <div className="flex flex-wrap gap-2">
                {result.matching_keywords.map((keyword, idx) => (
                  <span key={idx} className="inline-block px-3 py-1 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-medium border border-emerald-100">
                    {keyword}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-3 text-red-600 text-sm flex items-center gap-1.5">
                <span className="w-5 h-5 bg-red-100 rounded-md flex items-center justify-center text-xs">✗</span>
                Missing Keywords
              </h4>
              <div className="flex flex-wrap gap-2">
                {result.missing_keywords.map((keyword, idx) => (
                  <span key={idx} className="inline-block px-3 py-1 bg-red-50 text-red-700 rounded-lg text-xs font-medium border border-red-100">
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {result.searched_keywords && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8">
          <h3 className="text-lg font-bold mb-1 text-gray-900 flex items-center gap-2">
            <span className="w-7 h-7 bg-purple-100 rounded-lg flex items-center justify-center text-sm">🔍</span>
            Internet Keyword Search Results
          </h3>
          <p className="text-xs text-gray-400 mb-5">Source: {result.searched_keywords.source}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {result.searched_keywords.jd_skills_found?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2.5 text-indigo-700 text-sm">📋 Job Description Skills</h4>
                <div className="flex flex-wrap gap-1.5">
                  {result.searched_keywords.jd_skills_found.map((skill, idx) => (
                    <span key={idx} className="inline-block px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-lg text-xs font-medium border border-indigo-100">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {result.searched_keywords.trending_skills?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2.5 text-purple-700 text-sm">🔥 Trending Skills (Web)</h4>
                <div className="flex flex-wrap gap-1.5">
                  {result.searched_keywords.trending_skills.map((skill, idx) => (
                    <span key={idx} className="inline-block px-2.5 py-1 bg-purple-50 text-purple-700 rounded-lg text-xs font-medium border border-purple-100">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {result.searched_keywords.industry_terms?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2.5 text-blue-700 text-sm">🏢 Industry Terms</h4>
                <div className="flex flex-wrap gap-1.5">
                  {result.searched_keywords.industry_terms.map((term, idx) => (
                    <span key={idx} className="inline-block px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg text-xs font-medium border border-blue-100">
                      {term}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {result.searched_keywords.jd_soft_skills?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2.5 text-teal-700 text-sm">🤝 Soft Skills Detected</h4>
                <div className="flex flex-wrap gap-1.5">
                  {result.searched_keywords.jd_soft_skills.map((skill, idx) => (
                    <span key={idx} className="inline-block px-2.5 py-1 bg-teal-50 text-teal-700 rounded-lg text-xs font-medium border border-teal-100">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {result.searched_keywords.action_verbs?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2.5 text-amber-700 text-sm">⚡ Recommended Action Verbs</h4>
                <div className="flex flex-wrap gap-1.5">
                  {result.searched_keywords.action_verbs.map((verb, idx) => (
                    <span key={idx} className="inline-block px-2.5 py-1 bg-amber-50 text-amber-700 rounded-lg text-xs font-medium border border-amber-100">
                      {verb}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {result.recommendations && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8">
          <h3 className="text-lg font-bold mb-4 text-gray-900">Recommendations</h3>
          <div className="bg-indigo-50/50 rounded-xl p-4 border border-indigo-100">
            {Array.isArray(result.recommendations) ? (
              <ul className="space-y-2">
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-gray-700 text-sm flex items-start gap-2">
                    <span className="text-indigo-500 font-bold flex-shrink-0">→</span>
                    {rec}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-700 text-sm">{result.recommendations}</p>
            )}
          </div>
        </div>
      )}

      {result.modifications && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8">
          <h3 className="text-lg font-bold mb-4 text-gray-900">Modifications Made</h3>
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            {Array.isArray(result.modifications) ? (
              <ul className="space-y-2">
                {result.modifications.map((mod, idx) => (
                  <li key={idx} className="text-gray-700 text-sm flex items-start gap-2">
                    <span className="text-emerald-500 font-bold flex-shrink-0">•</span>
                    {mod}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-700 text-sm whitespace-pre-wrap">{result.modifications}</p>
            )}
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8">
        <h3 className="text-lg font-bold mb-4 text-gray-900">Tailored CV Preview</h3>
        <div className="bg-gray-50 rounded-xl p-5 mb-5 max-h-96 overflow-y-auto border border-gray-200">
          <pre className="text-sm text-gray-700 whitespace-pre-wrap break-words font-sans leading-relaxed">
            {result.tailored_cv?.substring(0, 1500)}
            {result.tailored_cv && result.tailored_cv.length > 1500 ? '\n\n[... CV continues ...]' : ''}
          </pre>
        </div>

        <div className="flex gap-3 flex-wrap">
          <button
            onClick={() => setShowFullDocument(true)}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium text-sm hover:shadow-lg hover:shadow-indigo-200 transition-all"
          >
            <Eye size={16} />
            View Full Document
          </button>

          <button
            onClick={handleGeneratePDF}
            disabled={isGeneratingPDF}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-xl font-medium text-sm hover:shadow-lg hover:shadow-green-200 disabled:opacity-50 transition-all"
          >
            {isGeneratingPDF ? (
              <>
                <Loader size={16} className="animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Download size={16} />
                Download PDF
              </>
            )}
          </button>

          <button
            onClick={handleCopyCV}
            className="flex items-center gap-2 px-5 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium text-sm hover:bg-gray-50 transition-colors"
          >
            <Copy size={16} />
            {copySuccess ? 'Copied!' : 'Copy Text'}
          </button>
        </div>
      </div>

      {/* Full Document Modal */}
      {showFullDocument && (
        <div 
          className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={() => setShowFullDocument(false)}
        >
          <div 
            className="bg-white rounded-2xl max-w-4xl w-full max-h-[80vh] overflow-y-auto shadow-2xl slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white/90 backdrop-blur-lg border-b border-gray-100 p-5 flex items-center justify-between rounded-t-2xl">
              <h2 className="text-xl font-bold text-gray-900">Full Tailored CV</h2>
              <button
                onClick={() => setShowFullDocument(false)}
                className="p-2 hover:bg-gray-100 rounded-xl transition"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-6 sm:p-8">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap break-words font-sans leading-relaxed">
                {result.tailored_cv}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
