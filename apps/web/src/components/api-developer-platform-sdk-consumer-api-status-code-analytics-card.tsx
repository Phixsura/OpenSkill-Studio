"use client";

interface CodeBucket { statusCode: number; count: number; percentage: number; category: string; }
interface Props { totalRequests: number; successRate: number; clientErrorRate: number; serverErrorRate: number; byCategory: Record<string, number>; topCodes: CodeBucket[]; consumerId: string; appName: string; }

const catColors: Record<string, string> = { "2xx": "bg-green-500", "3xx": "bg-blue-500", "4xx": "bg-amber-500", "5xx": "bg-red-500" };

export default function APIDeveloperPlatformSDKConsumerApiStatusCodeAnalyticsCard({ totalRequests, successRate, clientErrorRate, serverErrorRate, byCategory, topCodes, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Status Code Analytics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {totalRequests.toLocaleString()} requests</p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{successRate}%</div><div className="text-[9px] text-gray-400">Success</div></div>
        <div className="rounded bg-amber-50 p-1.5 dark:bg-amber-900/20"><div className="font-bold text-amber-600">{clientErrorRate}%</div><div className="text-[9px] text-gray-400">4xx</div></div>
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">{serverErrorRate}%</div><div className="text-[9px] text-gray-400">5xx</div></div>
      </div>
      {Object.keys(byCategory).length > 0 && (
        <div className="mb-2 flex h-3 overflow-hidden rounded-full bg-gray-200">
          {Object.entries(byCategory).filter(([_, v]) => v > 0).map(([cat, count]) => (
            <div key={cat} className={`${catColors[cat] ?? "bg-gray-400"}`} style={{ width: `${(count / totalRequests) * 100}%` }} title={`${cat}: ${count}`} />
          ))}
        </div>
      )}
      {topCodes.length > 0 && (
        <div className="space-y-0.5">
          {topCodes.slice(0, 5).map((c) => (
            <div key={c.statusCode} className="flex justify-between text-[10px]"><span className="text-gray-700 dark:text-gray-300">{c.statusCode}</span><span className="text-gray-400">{c.count.toLocaleString()} ({c.percentage}%)</span></div>
          ))}
        </div>
      )}
    </div>
  );
}
