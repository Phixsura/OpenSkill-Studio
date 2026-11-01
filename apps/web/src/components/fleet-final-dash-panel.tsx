"use client";
const SC: Record<string, string> = { operational: "text-green-600", degraded: "text-yellow-600", critical: "text-red-500" };
export function FleetFinalDashPanel({ services, files, lines, healthPct, status }: { services: number; files: number; lines: number; healthPct: number; status: string; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6">
    <h3 className="font-semibold mb-2 text-center">🏢 Platform Dashboard</h3>
    <div className={`text-center text-xl font-bold ${SC[status] ?? ""}`}>{status.toUpperCase()} — {healthPct}%</div>
    <div className="grid grid-cols-3 gap-2 mt-3 text-center text-xs text-gray-400">
      <div><div className="font-bold text-lg">{services.toLocaleString()}</div>services</div>
      <div><div className="font-bold text-lg">{files.toLocaleString()}</div>files</div>
      <div><div className="font-bold text-lg">{lines.toLocaleString()}</div>lines</div>
    </div>
  </div>);
}
