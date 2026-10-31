"use client";

interface Provider { id: string; name: string; status: string; latencyMs: number; error: string; }
interface Props { providers: Provider[]; overall: string; operational: number; degraded: number; outage: number; appName: string; }

const statusDot: Record<string, string> = { operational: "bg-green-500", degraded: "bg-amber-500", outage: "bg-red-500", maintenance: "bg-blue-500" };
const overallColors: Record<string, string> = { operational: "bg-green-100 text-green-700", degraded: "bg-amber-100 text-amber-700", outage: "bg-red-100 text-red-700" };

export default function APIDeveloperPlatformSDKConsumerApiProviderIntegrationStatusCard({ providers, overall, operational, degraded, outage, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔌 Provider Status</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {operational}↑ {degraded}~ {outage}↓</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[10px] font-bold ${overallColors[overall] ?? ""}`}>{overall}</span>
      </div>
      {providers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No providers</p>
      ) : (
        <div className="space-y-1">
          {providers.map((p) => (
            <div key={p.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${statusDot[p.status] ?? ""}`} />
                <span className="text-gray-700 dark:text-gray-300">{p.name}</span>
              </div>
              <span className="text-[10px] text-gray-400">{p.latencyMs}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
