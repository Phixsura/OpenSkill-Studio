"use client";

interface ScoreInfo { endpoint: string; composite_score: number; grade: string; availability_score: number; latency_score: number; error_rate_score: number; documentation_score: number; }
interface Props { scores: ScoreInfo[]; failingCount: number; appName: string; }

const gColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-orange-600", F: "text-red-600" };

export default function APIDeveloperAPIApiEndpointScoringCard({ scores, failingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏅 Endpoint Scores</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {failingCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{failingCount} failing</span>}
      </div>
      {scores.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No scores</p>
      ) : (
        <div className="space-y-1.5">
          {scores.map((s) => (
            <div key={s.endpoint} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-2">
                <span className={`text-sm font-black ${gColor[s.grade] ?? "text-gray-500"}`}>{s.grade}</span>
                <span className="text-gray-700 dark:text-gray-300">{s.endpoint}</span>
              </div>
              <span className="text-gray-400">{s.composite_score}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
