"use client";

interface CronJob { id: string; name: string; schedule: string; enabled: boolean;
  lastStatus: string | null; runCount: number; failCount: number; successRate: number; }
interface CronJobTableProps { jobs: CronJob[]; onToggle: (id: string) => void; }

export function CronJobTable({ jobs, onToggle }: CronJobTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏰ Cron Jobs</h3>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-left text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3">Name</th><th className="p-3">Schedule</th>
          <th className="p-3">Runs</th><th className="p-3">Rate</th>
          <th className="p-3">Status</th><th className="p-3">Active</th>
        </tr></thead>
        <tbody>
          {jobs.map(j => (
            <tr key={j.id} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 font-medium">{j.name}</td>
              <td className="p-3 font-mono text-xs text-gray-400">{j.schedule}</td>
              <td className="p-3 text-xs">{j.runCount}</td>
              <td className="p-3 text-xs">{j.successRate}%</td>
              <td className="p-3">
                {j.lastStatus && (
                  <span className={`text-xs px-1.5 py-0.5 rounded ${j.lastStatus === "success" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {j.lastStatus}
                  </span>
                )}
              </td>
              <td className="p-3">
                <button onClick={() => onToggle(j.id)}
                  className={`w-8 h-4 rounded-full transition ${j.enabled ? "bg-blue-500" : "bg-gray-300"}`}>
                  <span className={`block w-3 h-3 rounded-full bg-white transition transform ${j.enabled ? "translate-x-4" : "translate-x-0.5"}`} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
