"use client";

interface ScoreInfo { endpoint_coverage_pct: number; example_coverage_pct: number; error_doc_coverage_pct: number; overall_score: number; grade: string; guide_count: number; }
interface Props { score: ScoreInfo; appName: string; }

const gColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-500" };

export default function APIDeveloperAPIDocumentationScoreCard({ score: s, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📖 Doc Score</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-2xl font-bold ${gColor[s.grade] ?? "text-gray-500"}`}>{s.grade}</span>
          <p className="text-[10px] text-gray-400">{s.overall_score}%</p>
        </div>
      </div>
      <div className="space-y-1.5">
        {[
          { l: "Endpoints", v: s.endpoint_coverage_pct },
          { l: "Examples", v: s.example_coverage_pct },
          { l: "Error Docs", v: s.error_doc_coverage_pct },
        ].map((m) => (
          <div key={m.l}>
            <div className="flex justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{m.l}</span>
              <span className="text-gray-400">{m.v}%</span>
            </div>
            <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
              <div className={`h-1 rounded-full ${m.v >= 90 ? "bg-green-500" : m.v >= 70 ? "bg-yellow-500" : "bg-red-500"}`} style={{ width: `${m.v}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
