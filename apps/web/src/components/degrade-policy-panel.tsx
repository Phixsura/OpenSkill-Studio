"use client";
interface DegradePolicyPanelProps { activeTier: string; degraded: boolean; actions: string[];
  triggeredCount: number; }
const TIER_COLOR: Record<string, string> = { normal: "bg-green-500", minor: "bg-yellow-500",
  moderate: "bg-orange-500", severe: "bg-red-500", emergency: "bg-red-700" };
export function DegradePolicyPanel({ activeTier, degraded, actions, triggeredCount }: DegradePolicyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${TIER_COLOR[activeTier] ?? "bg-gray-500"}`}>
        {degraded ? `⚠ ${activeTier.toUpperCase()} DEGRADATION · ${triggeredCount} policies` : "✅ NORMAL OPERATION"}
      </div>
      {actions.length > 0 && (
        <div className="p-3 flex flex-wrap gap-1">
          {actions.map(a => <span key={a} className="text-[10px] px-1.5 py-0.5 rounded bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300">{a}</span>)}
        </div>
      )}
    </div>
  );
}
