"use client";

interface AssessmentInfo { change_id: string; endpoint: string; change_type: string; risk_level: string; breaking: boolean; affected_count: number; impact_score: number; }
interface Props { assessments: AssessmentInfo[]; breakingCount: number; highRiskCount: number; appName: string; }

const rColor: Record<string, string> = { low: "bg-green-100 text-green-700", medium: "bg-yellow-100 text-yellow-700", high: "bg-orange-100 text-orange-700", critical: "bg-red-100 text-red-700" };

export default function APIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzerCard({ assessments, breakingCount, highRiskCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💥 Impact Analyzer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2">
          {breakingCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{breakingCount} breaking</span>}
          {highRiskCount > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{highRiskCount} high risk</span>}
        </div>
      </div>
      {assessments.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No impact assessments</p>
      ) : (
        <div className="space-y-1.5">
          {assessments.map((a) => (
            <div key={a.change_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] ${rColor[a.risk_level] ?? ""}`}>{a.risk_level}</span>
                <span className="text-gray-700 dark:text-gray-300">{a.endpoint}</span>
              </div>
              <span className="text-gray-400">{a.change_type} · {a.affected_count} affected</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
