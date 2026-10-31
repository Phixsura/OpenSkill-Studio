"use client";

interface ShutdownStateInfo {
  phase: "running" | "draining" | "shutdown";
  in_flight_requests: number;
  drain_timeout_seconds: number;
  hooks_registered: number;
  hooks_completed: number;
  ready_to_shutdown: boolean;
}

interface GracefulShutdownCardProps {
  state: ShutdownStateInfo;
  appName: string;
}

const PHASE_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  running: {
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
    label: "Running",
  },
  draining: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
    label: "Draining",
  },
  shutdown: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-600 dark:text-gray-400",
    label: "Shutdown",
  },
};

export default function GracefulShutdownCard({ state, appName }: GracefulShutdownCardProps) {
  const phase = PHASE_STYLES[state.phase] ?? PHASE_STYLES.running;
  const hooksPct =
    state.hooks_registered > 0
      ? Math.round((state.hooks_completed / state.hooks_registered) * 100)
      : 100;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Shutdown Status
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${phase.bg} ${phase.text}`}>
          {phase.label}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <div>
          <p className="text-lg font-bold text-gray-800 dark:text-gray-200">
            {state.in_flight_requests}
          </p>
          <p className="text-[10px] text-gray-500">In-flight</p>
        </div>
        <div>
          <p className="text-lg font-bold text-gray-800 dark:text-gray-200">
            {state.hooks_completed}/{state.hooks_registered}
          </p>
          <p className="text-[10px] text-gray-500">Hooks</p>
        </div>
        <div>
          <p className="text-lg font-bold text-gray-800 dark:text-gray-200">
            {state.drain_timeout_seconds}s
          </p>
          <p className="text-[10px] text-gray-500">Timeout</p>
        </div>
      </div>

      {state.phase === "draining" && (
        <div className="mt-3">
          <div className="mb-0.5 text-[11px] text-gray-400">Hook progress</div>
          <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className="h-2 rounded-full bg-yellow-500" style={{ width: `${hooksPct}%` }} />
          </div>
        </div>
      )}

      {state.ready_to_shutdown && state.phase === "draining" && (
        <p className="mt-2 text-center text-xs font-medium text-green-600 dark:text-green-400">
          Ready to shutdown
        </p>
      )}
    </div>
  );
}
