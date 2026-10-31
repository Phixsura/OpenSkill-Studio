"use client";

interface CircuitInfo { service: string; state: string; critical: boolean; }
interface CircuitHealthDashProps { circuits: CircuitInfo[]; overall: string;
  openPct: number; criticalOpen: string[]; }

const STATE_COLOR: Record<string, string> = {
  closed: "bg-green-500", open: "bg-red-500", "half-open": "bg-yellow-500",
};

export function CircuitHealthDash({ circuits, overall, openPct, criticalOpen }: CircuitHealthDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Circuit Health</h3>
        <span className={`text-xs font-bold uppercase ${overall === "healthy" ? "text-green-600" : overall === "critical" ? "text-red-600" : "text-yellow-600"}`}>
          {overall} · {openPct}% open
        </span>
      </div>
      {criticalOpen.length > 0 && (
        <div className="px-4 py-2 text-xs text-red-600 bg-red-50 dark:bg-red-950">
          Critical: {criticalOpen.join(", ")}
        </div>
      )}
      <div className="flex flex-wrap gap-2 p-4">
        {circuits.map(c => (
          <div key={c.service} className="flex items-center gap-1 text-xs">
            <span className={`w-2.5 h-2.5 rounded-full ${STATE_COLOR[c.state] ?? "bg-gray-400"}`} />
            <span className={c.critical ? "font-bold" : ""}>{c.service}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
