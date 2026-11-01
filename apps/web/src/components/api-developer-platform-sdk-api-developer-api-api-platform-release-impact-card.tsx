"use client";

interface ImpactInfo { version: string; error_delta: number; latency_delta_ms: number; impact_severity: string; consumers_affected: number; rollback_needed: boolean; }
interface Props { impacts: ImpactInfo[]; highImpactCount: number; appName: string; }

const sColor: Record<string, string> = { low: "bg-green-100 text-green-700", medium: "bg-yellow-100 text-yellow-700", high: "bg-orange-100 text-orange-700", critical: "bg-red-100 text-red-700" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpactCard({ impacts, highImpactCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💥 Release Impact</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {highImpactCount > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{highImpactCount} high impact</span>}
      </div>
      {impacts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No release impacts</p>
      ) : (
        <div className="space-y-2">
          {impacts.map((i) => (
            <div key={i.version} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-gray-700 dark:text-gray-300">{i.version}</span>
                  <span className={`rounded px-1 py-0.5 text-[9px] ${sColor[i.impact_severity] ?? ""}`}>{i.impact_severity}</span>
                  {i.rollback_needed && <span className="text-[9px] text-red-500 font-bold">ROLLBACK</span>}
                </div>
                <span className="text-gray-400">{i.consumers_affected} affected</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>errors: {i.error_delta > 0 ? "+" : ""}{i.error_delta}%</span>
                <span>latency: {i.latency_delta_ms > 0 ? "+" : ""}{i.latency_delta_ms}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
