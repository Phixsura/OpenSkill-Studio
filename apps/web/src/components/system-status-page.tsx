"use client";

interface ServiceStatus { name: string; status: string; uptime: number; }
interface SystemStatusPageProps { overall: string; overallIcon: string;
  services: ServiceStatus[]; avgUptimeDisplay: string; lastIncident: string; }

export function SystemStatusPage({ overall, overallIcon, services, avgUptimeDisplay, lastIncident }: SystemStatusPageProps) {
  return (
    <div className="max-w-2xl mx-auto">
      <div className={`rounded-xl p-6 text-center text-white mb-6 ${
        overall.includes("Operational") ? "bg-green-600" : "bg-yellow-600"
      }`}>
        <p className="text-3xl mb-1">{overallIcon}</p>
        <h1 className="text-xl font-bold">{overall}</h1>
        <p className="text-sm opacity-90">Avg uptime: {avgUptimeDisplay}</p>
      </div>
      <div className="rounded-xl border dark:border-gray-700">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-3 border-b last:border-0 dark:border-gray-700">
            <span className="text-sm font-medium">{s.name}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">{s.uptime}%</span>
              <span className={`w-2.5 h-2.5 rounded-full ${s.status === "operational" ? "bg-green-500" : "bg-yellow-500"}`} />
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-400 text-center mt-4">{lastIncident}</p>
    </div>
  );
}
