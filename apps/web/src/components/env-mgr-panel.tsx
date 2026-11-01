"use client";

interface EnvInfo { name: string; tier: string; region: string; status: string; services: number; }
interface EnvMgrPanelProps { environments: EnvInfo[]; }

const TIER_STYLE: Record<string, string> = {
  standard: "bg-gray-100 text-gray-700", premium: "bg-purple-100 text-purple-700",
};
const STATUS_DOT: Record<string, string> = {
  active: "bg-green-500", provisioning: "bg-yellow-500", decommissioned: "bg-gray-400",
};

export function EnvMgrPanel({ environments }: EnvMgrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌍 Environments</h3>
        <span className="text-xs text-gray-400">{environments.length} environments</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {environments.map(e => (
          <div key={e.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${STATUS_DOT[e.status] ?? "bg-gray-400"}`} />
              <span className="font-bold">{e.name}</span>
              <span className={`px-1 rounded text-[10px] ${TIER_STYLE[e.tier] ?? ""}`}>{e.tier}</span>
            </div>
            <span className="text-gray-400">{e.region} · {e.services} services</span>
          </div>
        ))}
      </div>
    </div>
  );
}
