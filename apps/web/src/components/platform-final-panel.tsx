"use client";
interface PlatformFinalPanelProps { overall: string; score: number; modulesOperational: number;
  totalModules: number; uptimePct: number; errorRatePct: number; rps: number; p99Ms: number; }
const OV_COLOR: Record<string, string> = { fully_operational: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function PlatformFinalPanel({ overall, score, modulesOperational, totalModules,
  uptimePct, errorRatePct, rps, p99Ms }: PlatformFinalPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${OV_COLOR[overall] ?? "bg-gray-500"}`}>
        <div className="text-3xl font-black">{score}/100</div>
        <div className="text-sm">OpenSkill Platform: {overall.replace("_", " ").toUpperCase()}</div>
        <div className="text-xs opacity-80">{modulesOperational}/{totalModules} modules · {rps.toLocaleString()} rps</div>
      </div>
      <div className="grid grid-cols-4 gap-1 p-4 text-center text-[11px]">
        <div><span className="text-gray-400">Uptime</span><div className="font-bold">{uptimePct}%</div></div>
        <div><span className="text-gray-400">Errors</span><div className="font-bold">{errorRatePct}%</div></div>
        <div><span className="text-gray-400">P99</span><div className="font-bold">{p99Ms}ms</div></div>
        <div><span className="text-gray-400">Modules</span><div className="font-bold">{modulesOperational}/{totalModules}</div></div>
      </div>
    </div>
  );
}
