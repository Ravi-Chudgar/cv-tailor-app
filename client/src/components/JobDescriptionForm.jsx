import React, { useState } from 'react'
import { Send, Loader, AlertCircle, CheckCircle, XCircle, TrendingUp } from 'lucide-react'
import { jobAPI } from '../api/client'
import { useCVStore } from '../stores/cvStore'

export default function JobDescriptionForm({ selectedCVFile }) {
  const [jobDescription, setJobDescription] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [jobAnalysis, setJobAnalysis] = useState(null)
  const [gapAnalysis, setGapAnalysis] = useState(null)
  const { setJobDescription: setStoreJobDescription } = useCVStore()

  const handleAnalyze = async (e) => {
    e.preventDefault()

    if (!jobDescription.trim()) {
      setError('Please enter a job description')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      console.log('[JOB ANALYZE] Sending request with:', { descLength: jobDescription.length, cvFileId: selectedCVFile })
      const response = await jobAPI.analyze(jobDescription, '', '', selectedCVFile || '')
      console.log('[JOB ANALYZE] Response:', response.data)
      setJobAnalysis(response.data.analysis)
      setGapAnalysis(response.data.gap_analysis || null)
      setStoreJobDescription(jobDescription)
    } catch (err) {
      console.error('[JOB ANALYZE] Error:', err.response?.data || err.message)
      const detail = err.response?.data?.detail
      let errorMessage = 'Failed to analyze job description'
      
      if (Array.isArray(detail)) {
        errorMessage = detail.map(d => d.msg || d.toString()).join(', ')
      } else if (typeof detail === 'string') {
        errorMessage = detail
      } else if (err.response?.data) {
        errorMessage = JSON.stringify(err.response.data)
      }
      
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBg = (score) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 50) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8">
      <h2 className="text-xl font-bold mb-5 text-gray-900">Job Description Analysis</h2>

      <form onSubmit={handleAnalyze} className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-semibold mb-2 text-gray-700">Job Description</label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the complete job description here..."
            rows={8}
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition resize-none"
          />
        </div>

        {!selectedCVFile && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-800 flex gap-2 items-start">
            <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
            Select a CV above to see gap analysis (what's missing from your CV)
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium text-sm hover:shadow-lg hover:shadow-indigo-200 disabled:opacity-50 transition-all flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader size={16} className="animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Send size={16} />
              Analyze Job
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="p-3.5 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm mb-6">
          {error}
        </div>
      )}

      {/* Gap Analysis Section */}
      {gapAnalysis && (
        <div className="border-t border-gray-100 pt-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold flex items-center gap-2 text-gray-900">
              <TrendingUp size={20} className="text-indigo-600" />
              CV Gap Analysis
            </h3>
            {gapAnalysis.cv_name && (
              <span className="text-xs text-gray-400 bg-gray-100 px-2.5 py-1 rounded-lg">vs. {gapAnalysis.cv_name}</span>
            )}
          </div>

          {/* Score Bar */}
          <div className="mb-6 p-4 bg-gray-50 rounded-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-700 text-sm">Keyword Coverage</span>
              <span className={`text-2xl font-extrabold ${getScoreColor(gapAnalysis.gap_score)}`}>
                {gapAnalysis.gap_score}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${getScoreBg(gapAnalysis.gap_score)}`}
                style={{ width: `${gapAnalysis.gap_score}%` }}
              />
            </div>
            <p className="text-xs text-gray-400 mt-2">
              {gapAnalysis.total_matched} of {gapAnalysis.total_required} keywords found in your CV
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Found in CV */}
            {gapAnalysis.found_in_cv?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2.5 text-emerald-700 text-sm flex items-center gap-1.5">
                  <CheckCircle size={15} />
                  Already in Your CV ({gapAnalysis.found_in_cv.length})
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {gapAnalysis.found_in_cv.map((skill, idx) => (
                    <span key={idx} className="inline-block px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-medium border border-emerald-100">
                      ✓ {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing from CV */}
            {gapAnalysis.missing_from_cv?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2.5 text-red-600 text-sm flex items-center gap-1.5">
                  <XCircle size={15} />
                  Missing — Need to Add ({gapAnalysis.missing_from_cv.length})
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {gapAnalysis.missing_from_cv.map((skill, idx) => (
                    <span key={idx} className="inline-block px-2.5 py-1 bg-red-50 text-red-700 rounded-lg text-xs font-semibold border border-red-100">
                      ✗ {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Soft Skills */}
            {(gapAnalysis.soft_skills_found?.length > 0 || gapAnalysis.soft_skills_missing?.length > 0) && (
              <div>
                <h4 className="font-semibold mb-2.5 text-purple-700 text-sm">Soft Skills & Methodologies</h4>
                <div className="flex flex-wrap gap-1.5">
                  {gapAnalysis.soft_skills_found?.map((skill, idx) => (
                    <span key={`sf-${idx}`} className="inline-block px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-medium border border-emerald-100">
                      ✓ {skill}
                    </span>
                  ))}
                  {gapAnalysis.soft_skills_missing?.map((skill, idx) => (
                    <span key={`sm-${idx}`} className="inline-block px-2.5 py-1 bg-red-50 text-red-700 rounded-lg text-xs font-medium border border-red-100">
                      ✗ {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Certifications */}
            {(gapAnalysis.certs_found?.length > 0 || gapAnalysis.certs_missing?.length > 0) && (
              <div>
                <h4 className="font-semibold mb-2.5 text-amber-700 text-sm">Certifications</h4>
                <div className="flex flex-wrap gap-1.5">
                  {gapAnalysis.certs_found?.map((cert, idx) => (
                    <span key={`cf-${idx}`} className="inline-block px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-medium border border-emerald-100">
                      ✓ {cert}
                    </span>
                  ))}
                  {gapAnalysis.certs_missing?.map((cert, idx) => (
                    <span key={`cm-${idx}`} className="inline-block px-2.5 py-1 bg-red-50 text-red-700 rounded-lg text-xs font-medium border border-red-100">
                      ✗ {cert}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Recommendations */}
          {gapAnalysis.recommendations?.length > 0 && (
            <div className="mt-5 p-4 bg-indigo-50/50 border border-indigo-100 rounded-xl">
              <h4 className="font-semibold mb-2.5 text-indigo-800 text-sm">💡 Recommendations</h4>
              <ul className="space-y-1.5">
                {gapAnalysis.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-xs text-gray-700 flex items-start gap-2">
                    <span className="text-indigo-500 font-bold flex-shrink-0">→</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Job Analysis Keywords */}
      {jobAnalysis && (
        <div className="border-t border-gray-100 pt-6">
          <h3 className="text-lg font-bold mb-4 text-gray-900">Job Requirements Found</h3>

          <div className="space-y-4">
            {jobAnalysis.key_skills?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-sm text-gray-700">Technical Skills Required</h4>
                <div className="flex flex-wrap gap-1.5">
                  {jobAnalysis.key_skills.map((skill, idx) => (
                    <span key={idx} className="px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-lg text-xs font-medium border border-indigo-100">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {jobAnalysis.trending_skills?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-sm text-gray-700">🔥 Trending Skills (Web)</h4>
                <div className="flex flex-wrap gap-1.5">
                  {jobAnalysis.trending_skills.map((skill, idx) => (
                    <span key={idx} className="px-2.5 py-1 bg-purple-50 text-purple-700 rounded-lg text-xs font-medium border border-purple-100">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {jobAnalysis.soft_skills?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-sm text-gray-700">Soft Skills & Methodologies</h4>
                <div className="flex flex-wrap gap-1.5">
                  {jobAnalysis.soft_skills.map((skill, idx) => (
                    <span key={idx} className="px-2.5 py-1 bg-teal-50 text-teal-700 rounded-lg text-xs font-medium border border-teal-100">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {jobAnalysis.certifications?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-sm text-gray-700">Certifications</h4>
                <div className="flex flex-wrap gap-1.5">
                  {jobAnalysis.certifications.map((cert, idx) => (
                    <span key={idx} className="px-2.5 py-1 bg-amber-50 text-amber-700 rounded-lg text-xs font-medium border border-amber-100">
                      {cert}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {jobAnalysis.action_verbs?.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-sm text-gray-700">⚡ Recommended Action Verbs</h4>
                <div className="flex flex-wrap gap-1.5">
                  {jobAnalysis.action_verbs.map((verb, idx) => (
                    <span key={idx} className="px-2.5 py-1 bg-gray-100 text-gray-700 rounded-lg text-xs font-medium border border-gray-200">
                      {verb}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
