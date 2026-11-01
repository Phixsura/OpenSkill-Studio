"use client";

interface CheckInfo { name: string; passed: boolean; required: boolean; }
interface Props { version: string; checks: CheckInfo[]; readinessPct: number; verdict: string; appName: string; }

const vBanner: Record<string, string> = { SHIP_IT: "bg-green-50 text-green-700 border-green-200", SHIP_WITH_CAVEATS: "bg-yellow-50 text-yellow-700 border-yellow-200", HOLD: "bg-red-50 text-red-700 border-red-200" };

export default function APIDeveloperPlatformSDKApiPlatformReleaseReadinessCard({ version, checks, readinessPct, verdict, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-gray-200 bg-white p-5 shadow-lg dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">🚀 Release Readiness</h3>
        <p className="text-xs text-gray-500">{appName} · {version}</p>
      </div>
      <div className={`mb-3 rounded-lg border px-3 py-2 text-center text-sm font-black ${vBanner[verdict] ?? ""}`}>{verdict.replace(/_/g, " ")}</div>
      <div className="mb-3 h-2 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className={`h-2 rounded-full ${readinessPct === 100 ? "bg-green-500" : "bg-yellow-500"}`} style={{ width: `${readinessPct}%` }} />
      </div>
      <div className="space-y-1">
        {checks.map((c) => (
          <div key={c.name} className="flex items-center gap-2 text-[11px]">
            <span className={c.passed ? "text-green-500" : "text-red-400"}>{c.passed ? "✓" : "✗"}</span>
            <span className={c.passed ? "text-gray-400" : "text-gray-700 dark:text-gray-300"}>{c.name}</span>
            {c.required && !c.passed && <span className="text-[9px] text-red-500">required</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
