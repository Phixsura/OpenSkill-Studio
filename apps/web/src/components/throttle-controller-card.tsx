"use client";

interface ThrottleState {
  load_level: "low" | "medium" | "high" | "critical";
  current_load: number;
  allowed_rps: number;
  max_rps: number;
  throttle_pct: number;
}

interface ThrottleControllerCardProps {
  state: ThrottleState;
  appName: string;
}

const LEVEL_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  low: {
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
    label: "Low",
  },
  medium: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
    label: "Medium",
  },
  high: {
    bg: "bg-orange-100 dark:bg-orange-900/30",
    text: "text-orange-700 dark:text-orange-400",
    label: "High",
  },
  critical: {
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
    label: "Critical",
  },
};

function LoadGauge({ load }: { load: number }) {
  const pct = Math.min(load * 100, 100);
  const color =
    pct >= 95
      ? "bg-red-500"
      : pct >= 85
        ? "bg-orange-500"
        : pct >= 70
          ? "bg-yellow-500"
          : "bg-green-500";
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[11px] text-gray-500">
        <span>System Load</span>
        <span>{(load * 100).toFixed(0)}%</span>
      </div>
      <div className="h-2.5 rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className={`h-2.5 rounded-full transition-all ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function ThrottleControllerCard({ state, appName }: ThrottleControllerCardProps) {
  const level = LEVEL_STYLES[state.load_level] ?? LEVEL_STYLES.low;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Throttle Control
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${level.bg} ${level.text}`}
        >
          {level.label}
        </span>
      </div>

      <LoadGauge load={state.current_load} />

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div>
          <p className="text-lg font-bold text-gray-800 dark:text-gray-200">{state.allowed_rps}</p>
          <p className="text-[10px] text-gray-500">Allowed RPS</p>
        </div>
        <div>
          <p className="text-lg font-bold text-gray-800 dark:text-gray-200">{state.max_rps}</p>
          <p className="text-[10px] text-gray-500">Max RPS</p>
        </div>
        <div>
          <p
            className={`text-lg font-bold ${state.throttle_pct < 50 ? "text-red-600 dark:text-red-400" : "text-gray-800 dark:text-gray-200"}`}
          >
            {state.throttle_pct}%
          </p>
          <p className="text-[10px] text-gray-500">Throughput</p>
        </div>
      </div>
    </div>
  );
}
