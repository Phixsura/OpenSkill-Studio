"use client";
interface Change { current: number; previous: number; delta: number; improved: boolean; }
interface HealthComparePanelProps { service: string; overall: string; changes: Record<string, Change>; }
const OV_COLOR: Record<string, string> = { improved: "text-green-600", degraded: "text-red-500", stable: "text-gray-400" };
export function HealthComparePanel({ service, overall, changes }: HealthComparePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Health Compare: {service}</h3>
        <span className={`text-xs font-bold ${OV_COLOR[overall] ?? ""}`}>{overall}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(changes).map(([key, c]) => (
          <div key={key} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="text-gray-500">{key.replace(/_/g, " ")}</span>
            <span className={c.improved ? "text-green-600" : "text-red-500"}>
              {c.current} ({c.delta > 0 ? "+" : ""}{c.delta}) {c.improved ? "↑" : "↓"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
