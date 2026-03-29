import React from 'react'
import { TrendingUp, AlertCircle, CheckCircle, Award } from 'lucide-react'

export default function ATSScoreDisplay({ atsScore }) {
  if (!atsScore) return null

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-50'
    if (score >= 60) return 'bg-yellow-50'
    return 'bg-red-50'
  }

  const getBarColor = (score) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getGradeBg = (grade) => {
    if (grade?.startsWith('A')) return 'bg-green-600'
    if (grade === 'B') return 'bg-blue-600'
    if (grade === 'C') return 'bg-yellow-600'
    return 'bg-red-600'
  }

  const componentLabels = {
    keyword_match: 'Keyword Match',
    formatting: 'Formatting & Structure',
    impact_content: 'Impact & Content',
    ats_compatibility: 'ATS Compatibility',
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">ATS Score</h2>
        <div className="flex items-center gap-3">
          {atsScore.grade && (
            <span className={`${getGradeBg(atsScore.grade)} text-white text-sm font-bold px-3 py-1.5 rounded-xl`}>
              {atsScore.grade}
            </span>
          )}
        </div>
      </div>

      <div className="mb-8">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${getBarColor(atsScore.overall_score)}`}
                style={{ width: `${atsScore.overall_score}%` }}
              />
            </div>
          </div>
          <span className={`text-4xl font-extrabold ${getScoreColor(atsScore.overall_score)}`}>
            {atsScore.overall_score}
          </span>
        </div>
      </div>

      {atsScore.component_scores && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {Object.entries(atsScore.component_scores).map(([key, value]) => (
            <div key={key} className="bg-gray-50 rounded-xl p-4">
              <p className="text-xs font-semibold text-gray-500 mb-1">
                {componentLabels[key] || key.replace(/_/g, ' ').toUpperCase()}
              </p>
              {atsScore.weights && atsScore.weights[key] && (
                <p className="text-[10px] text-gray-400 mb-2">Weight: {atsScore.weights[key]}</p>
              )}
              <div className="flex items-center gap-2">
                <p className={`text-xl font-extrabold ${getScoreColor(value)}`}>{Math.round(value)}</p>
                <div className="flex-1 bg-gray-200 rounded-full h-1.5 overflow-hidden">
                  <div className={`h-full rounded-full ${getBarColor(value)}`} style={{ width: `${value}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {atsScore.recommendations && (
        <div className="bg-indigo-50/50 rounded-xl p-4 border border-indigo-100">
          <h3 className="font-semibold mb-2.5 text-sm flex items-center gap-2 text-gray-900">
            <AlertCircle size={16} className="text-indigo-600" />
            Recommendations
          </h3>
          <ul className="space-y-1.5">
            {atsScore.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-gray-700">
                <CheckCircle size={13} className="text-emerald-500 mt-0.5 flex-shrink-0" />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
