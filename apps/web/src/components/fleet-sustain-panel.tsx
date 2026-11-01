"use client";
const GC: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600" };
export function FleetSustainPanel({ carbonKg, renewablePct, pue, grade }: { carbonKg: number; renewablePct: number; pue: number; grade: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌱 Sustainability</h3>
    <div className={`text-lg font-bold ${GC[grade] ?? ""}`}>Grade {grade}</div>
    <div className="text-xs text-gray-400">{renewablePct}% renewable · PUE {pue} · {carbonKg}kg CO₂/mo</div>
  </div>);
}
