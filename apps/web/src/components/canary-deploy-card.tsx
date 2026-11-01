"use client";

interface CanaryDeployCardProps { verdict: string; errorDelta: number;
  latencyDeltaPct: number; errOk: boolean; latOk: boolean;
  baselineTraffic: number; canaryTraffic: number; }

const VERDICT_STYLE: Record<string, string> = {
  promote: "text-green-600", rollback: "text-red-600", hold: "text-yellow-600",
};

export function CanaryDeployCard({ verdict, errorDelta, latencyDeltaPct,
  errOk, latOk, baselineTraffic, canaryTraffic }: CanaryDeployCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐤 Canary Analysis</h3>
        <span className={`text-sm font-bold uppercase ${VERDICT_STYLE[verdict] ?? ""}`}>{verdict}</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-xs">
        <div>
          <div className="text-gray-400 mb-0.5">Error Rate Delta</div>
          <div className={errOk ? "text-green-600" : "text-red-600"}>{errorDelta > 0 ? "+" : ""}{errorDelta}%</div>
        </div>
        <div>
          <div className="text-gray-400 mb-0.5">Latency Delta</div>
          <div className={latOk ? "text-green-600" : "text-red-600"}>{latencyDeltaPct > 0 ? "+" : ""}{latencyDeltaPct}%</div>
        </div>
        <div>
          <div className="text-gray-400 mb-0.5">Baseline Traffic</div>
          <div>{baselineTraffic.toLocaleString()}</div>
        </div>
        <div>
          <div className="text-gray-400 mb-0.5">Canary Traffic</div>
          <div>{canaryTraffic.toLocaleString()}</div>
        </div>
      </div>
    </div>
  );
}
