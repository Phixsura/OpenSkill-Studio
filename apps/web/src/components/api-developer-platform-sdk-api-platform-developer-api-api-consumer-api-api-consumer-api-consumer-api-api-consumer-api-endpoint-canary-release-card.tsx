"use client";

interface Release { id: string; endpoint: string; canaryVersion: string; stableVersion: string; weightPct: number; status: string; }
interface Analysis { safeToPromote: boolean; errorDelta: number; latencyDelta: number; recommendation: string; }
interface Props { releases: Release[]; analysis: Analysis | null; appName: string; }

const statusColors: Record<string, string> = {
  active: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  promoted: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  rolled_back: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointCanaryReleaseCard({ releases, analysis, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🐤 Canary Releases</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {releases.length} releases</p>
      </div>
      {releases.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No canary releases</p>
      ) : (
        <div className="mb-3 space-y-2">
          {releases.map((r) => (
            <div key={r.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{r.endpoint}</code>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusColors[r.status] ?? ""}`}>{r.status}</span>
              </div>
              <div className="mt-0.5 flex items-center gap-2 text-[10px] text-gray-400">
                <span>{r.stableVersion} → {r.canaryVersion}</span>
                <span className="font-bold text-blue-600">{r.weightPct}% canary</span>
              </div>
            </div>
          ))}
        </div>
      )}
      {analysis && (
        <div className={`rounded-lg p-2 text-[10px] ${analysis.safeToPromote ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
          <div className="font-medium">{analysis.safeToPromote ? "✅ Safe to promote" : "⚠️ Not safe"}</div>
          <div className="text-gray-500">{analysis.recommendation}</div>
        </div>
      )}
    </div>
  );
}
