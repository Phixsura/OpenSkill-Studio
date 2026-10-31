"use client";
const SC: Record<string, string> = { calm: "text-green-600", busy: "text-yellow-600", storm: "text-red-500" };
export function FleetOpsSumPanel({ incidentsOpen, deploysToday, alertsFiring, status }: { incidentsOpen: number; deploysToday: number; alertsFiring: number; status: string; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">🏢 Ops Summary</h3>
    <div className={`text-xl font-bold ${SC[status] ?? ""}`}>{status.toUpperCase()}</div>
    <div className="text-xs text-gray-400 mt-1">🚨 {incidentsOpen} incidents · 🚀 {deploysToday} deploys · 🔔 {alertsFiring} alerts</div>
  </div>);
}
