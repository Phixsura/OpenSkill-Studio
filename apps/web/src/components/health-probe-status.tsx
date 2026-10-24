"use client";

interface HealthProbeStatusProps { liveness: string; readiness: string; startup: string;
  failedChecks: string[]; }

const STATUS_COLOR: Record<string, string> = {
  ok: "bg-green-500", ready: "bg-green-500", complete: "bg-green-500",
  not_ready: "bg-yellow-500", in_progress: "bg-yellow-500",
};

export function HealthProbeStatus({ liveness, readiness, startup, failedChecks }: HealthProbeStatusProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏥 Health Probes</h3>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        {[["Liveness", liveness], ["Readiness", readiness], ["Startup", startup]].map(([label, status]) => (
          <div key={label as string}>
            <div className="text-gray-400 mb-1">{label}</div>
            <div className="flex items-center justify-center gap-1">
              <span className={`w-2.5 h-2.5 rounded-full ${STATUS_COLOR[status as string] ?? "bg-gray-400"}`} />
              <span className="font-bold">{status}</span>
            </div>
          </div>
        ))}
      </div>
      {failedChecks.length > 0 && (
        <div className="border-t dark:border-gray-700 p-3 text-xs text-red-500">
          Failed: {failedChecks.join(", ")}
        </div>
      )}
    </div>
  );
}
