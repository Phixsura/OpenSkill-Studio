"use client";

interface HealthCheck { status: string; latencyMs: number; message: string; }
interface HealthcheckEndpointProps { status: string; checks: Record<string, HealthCheck>;
  output: string; ready: boolean; notReadyDeps: string[]; }

export function HealthcheckEndpoint({ status, checks, output, ready, notReadyDeps }: HealthcheckEndpointProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${status === "pass" ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold text-sm">💚 Health Check</h3>
        <div className="flex gap-2 text-xs">
          <span className={status === "pass" ? "text-green-600" : "text-red-500"}>{status}</span>
          <span className={ready ? "text-green-600" : "text-yellow-600"}>{ready ? "ready" : "not ready"}</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(checks).map(([name, c]) => (
          <div key={name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${c.status === "up" ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-medium">{name}</span>
            </div>
            <span className="text-gray-400">{c.latencyMs}ms {c.message && `· ${c.message}`}</span>
          </div>
        ))}
      </div>
      <div className="p-3 text-xs text-gray-500">{output}</div>
      {notReadyDeps.length > 0 && (
        <div className="px-3 pb-2 text-[10px] text-red-500">Not ready: {notReadyDeps.join(", ")}</div>
      )}
    </div>
  );
}
