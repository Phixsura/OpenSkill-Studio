"use client";
interface AttestInfo { service: string; status: string; stale: boolean; ageSeconds: number; }
interface HealthAttestPanelProps { services: AttestInfo[]; healthy: number; stale: number; }
const DOT: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", stale: "bg-gray-400", unknown: "bg-gray-300" };
export function HealthAttestPanel({ services, healthy, stale }: HealthAttestPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Health Attestation</h3>
        <span className="text-xs text-gray-400">{healthy} healthy{stale > 0 ? ` · ${stale} stale` : ""}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${DOT[s.status] ?? "bg-gray-400"}`} />
              <span className="font-mono">{s.service}</span>
            </div>
            <span className="text-gray-400">{s.status} · {s.ageSeconds}s ago</span>
          </div>
        ))}
      </div>
    </div>
  );
}
