"use client";
interface HealthInfo { consumer_id: string; status: string; error_rate: number; total_requests: number; }
interface Props { consumers: HealthInfo[]; appName: string; }
const sDot: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", inactive: "bg-gray-400" };
export default function APIDeveloperAPIConsumerHealthCard({ consumers, appName }: Props) {
  const unhealthy = consumers.filter((c) => c.status !== "healthy").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div><h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏥 Consumer Health</h3><p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p></div>
        <div className="text-right"><span className="text-xs text-gray-400">{consumers.length} consumers</span>{unhealthy > 0 && <p className="text-[10px] text-red-500">{unhealthy} unhealthy</p>}</div>
      </div>
      {consumers.length === 0 ? (<p className="text-center text-sm text-gray-400">No consumers</p>) : (
        <div className="space-y-1">{consumers.map((c) => (<div key={c.consumer_id} className="flex items-center justify-between text-[11px]"><div className="flex items-center gap-1.5"><span className={`h-2 w-2 rounded-full ${sDot[c.status] ?? "bg-gray-400"}`} /><span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span></div><span className="text-gray-400">{c.error_rate}% err · {c.total_requests} reqs</span></div>))}</div>
      )}
    </div>
  );
}
