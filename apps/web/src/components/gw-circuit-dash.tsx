"use client";

interface CircuitInfo { service: string; state: string; failures: number; }
interface GwCircuitDashProps { circuits: CircuitInfo[]; openCount: number; total: number; }

const STATE_STYLE: Record<string, string> = {
  closed: "text-green-600", open: "text-red-600", "half-open": "text-yellow-600",
};

export function GwCircuitDash({ circuits, openCount, total }: GwCircuitDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Circuit Breakers</h3>
        <span className={`text-xs ${openCount > 0 ? "text-red-500" : "text-green-600"}`}>
          {openCount > 0 ? `${openCount}/${total} open` : `${total} healthy`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {circuits.map(c => (
          <div key={c.service} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono">{c.service}</span>
            <div className="flex items-center gap-2">
              {c.failures > 0 && <span className="text-gray-400">{c.failures} failures</span>}
              <span className={`font-bold uppercase ${STATE_STYLE[c.state] ?? ""}`}>{c.state}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
