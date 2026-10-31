"use client";

interface PerfInfo { avg_latency_ms: number; p50_ms: number; p95_ms: number; p99_ms: number; total_requests: number; requests_per_second: number; error_rate: number; performance_grade: string; slowest_endpoint: string; }
interface Props { performance: PerfInfo; appName: string; }

const gColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-500" };

export default function APIDeveloperAPIPerformanceOverviewCard({ performance: p, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Performance</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-2xl font-bold ${gColor[p.performance_grade] ?? "text-gray-500"}`}>{p.performance_grade}</span>
      </div>
      <div className="grid grid-cols-4 gap-1.5 text-center">
        {[
          { l: "Avg", v: `${p.avg_latency_ms}ms` },
          { l: "p50", v: `${p.p50_ms}ms` },
          { l: "p95", v: `${p.p95_ms}ms` },
          { l: "p99", v: `${p.p99_ms}ms` },
          { l: "RPS", v: p.requests_per_second.toLocaleString() },
          { l: "Requests", v: p.total_requests.toLocaleString() },
          { l: "Errors", v: `${p.error_rate}%` },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[7px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
