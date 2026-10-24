"use client";
interface Ownership { endpoint: string; team: string; oncall: string; tier: string; }
interface EpOwnershipPanelProps { endpoints: Ownership[]; teams: number; unownedCount: number; }
const TIER_STYLE: Record<string, string> = { critical: "text-red-500", standard: "text-gray-400" };
export function EpOwnershipPanel({ endpoints, teams, unownedCount }: EpOwnershipPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">👥 Endpoint Ownership</h3>
        <span className="text-xs text-gray-400">
          {endpoints.length} owned · {teams} teams{unownedCount > 0 ? ` · ⚠ ${unownedCount} unowned` : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(o => (
          <div key={o.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{o.endpoint}</span>
            <span className="text-gray-400">{o.team} · {o.oncall} <span className={TIER_STYLE[o.tier] ?? ""}>[{o.tier}]</span></span>
          </div>
        ))}
      </div>
    </div>
  );
}
