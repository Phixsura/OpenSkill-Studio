"use client";
const LC: Record<string, string> = { Elite: "text-green-600", High: "text-blue-500", Medium: "text-yellow-600", Low: "text-red-500" };
export function FleetDoraMttrPanel({ mttrHours, level }: { mttrHours: number; level: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ DORA: MTTR</h3>
    <div className={`text-lg font-bold ${LC[level] ?? ""}`}>{level}</div>
    <div className="text-xs text-gray-400">{mttrHours}h to restore</div>
  </div>);
}
