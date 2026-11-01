"use client";
interface Fingerprint { service: string; fingerprint: string; level: string; uptime: number; errorRate: number; p99Ms: number; }
interface HealthFingerprintPanelProps { fingerprints: Fingerprint[]; }
const LVL_DOT: Record<string, string> = { green: "bg-green-500", yellow: "bg-yellow-500", red: "bg-red-500" };
export function HealthFingerprintPanel({ fingerprints }: HealthFingerprintPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Health Fingerprints</h3>
        <span className="text-xs text-gray-400">{fingerprints.length} services</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {fingerprints.map(f => (
          <div key={f.service} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${LVL_DOT[f.level] ?? "bg-gray-400"}`} />
              <span className="font-mono">{f.service}</span>
              <span className="text-gray-400 font-mono text-[10px]">{f.fingerprint}</span>
            </div>
            <span className="text-gray-400">{f.uptime}% · {f.errorRate}% err · {f.p99Ms}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
