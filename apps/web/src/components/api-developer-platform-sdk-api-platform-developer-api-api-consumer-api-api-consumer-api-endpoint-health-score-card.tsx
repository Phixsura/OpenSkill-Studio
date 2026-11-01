"use client";

interface Score { path: string; score: number; grade: string; status: string; uptimeScore: number; latencyScore: number; errorScore: number; }
interface Props { scores: Score[]; appName: string; }

const gradeColors: Record<string, string> = {
  A: "text-green-600", B: "text-blue-600", C: "text-amber-600", D: "text-orange-600", F: "text-red-600",
};
const statusBg: Record<string, string> = {
  healthy: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  degraded: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  unhealthy: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointHealthScoreCard({ scores, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🩺 Endpoint Health</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {scores.length} endpoints</p>
      </div>
      {scores.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health data</p>
      ) : (
        <div className="space-y-2">
          {scores.map((s) => (
            <div key={s.path} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-2">
                  <span className={`text-lg font-bold ${gradeColors[s.grade] ?? ""}`}>{s.grade}</span>
                  <code className="text-gray-700 dark:text-gray-300">{s.path}</code>
                </div>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusBg[s.status] ?? ""}`}>{s.status}</span>
              </div>
              <div className="mt-1 text-[10px] text-gray-400">Score: {s.score} · Uptime: {s.uptimeScore} · Latency: {s.latencyScore} · Errors: {s.errorScore}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
