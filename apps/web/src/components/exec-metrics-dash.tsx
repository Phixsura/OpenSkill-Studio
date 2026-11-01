"use client";

interface TrendInfo { current: number; previous: number; pctChange: number; direction: string; }
interface ExecMetricsDashProps { health: string; uptimePct: number; errorRatePct: number;
  p99Ms: number; dailyUsers: number; dailyApiCalls: number;
  trends?: Record<string, TrendInfo>; }

const HEALTH_STYLE: Record<string, string> = { green: "bg-green-500", yellow: "bg-yellow-500", red: "bg-red-500" };

export function ExecMetricsDash({ health, uptimePct, errorRatePct, p99Ms, dailyUsers, dailyApiCalls }: ExecMetricsDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${HEALTH_STYLE[health] ?? "bg-gray-500"}`}>
        Platform Health: {health.toUpperCase()}
      </div>
      <div className="grid grid-cols-5 gap-2 p-4 text-center text-xs">
        <div><div className="text-gray-400">Uptime</div><div className="font-bold text-lg">{uptimePct}%</div></div>
        <div><div className="text-gray-400">Error Rate</div><div className="font-bold text-lg">{errorRatePct}%</div></div>
        <div><div className="text-gray-400">P99</div><div className="font-bold text-lg">{p99Ms}ms</div></div>
        <div><div className="text-gray-400">DAU</div><div className="font-bold text-lg">{dailyUsers.toLocaleString()}</div></div>
        <div><div className="text-gray-400">API/day</div><div className="font-bold text-lg">{dailyApiCalls.toLocaleString()}</div></div>
      </div>
    </div>
  );
}
