"use client";
interface ChainValidatePanelProps { valid: boolean; maxDepth: number; services: number;
  cycles: string[][]; depthLimit: number; }
export function ChainValidatePanel({ valid, maxDepth, services, cycles, depthLimit }: ChainValidatePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Chain Validator</h3>
        <span className={`text-xs font-bold ${valid ? "text-green-600" : "text-red-500"}`}>
          {valid ? "✅ Valid" : "❌ Invalid"} · depth {maxDepth}/{depthLimit} · {services} services
        </span>
      </div>
      {cycles.length > 0 && (
        <div className="p-3 text-xs text-red-600">
          {cycles.map((c, i) => <div key={i} className="font-mono">Cycle: {c.join(" → ")}</div>)}
        </div>
      )}
    </div>
  );
}
