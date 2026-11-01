"use client";

interface ShutdownState {
  phase: "running" | "draining" | "cleanup" | "terminated" | "force_killed";
  hooksExecuted: number;
  hooksFailed: number;
  resourcesCleaned: string[];
  durationMs: number;
}

const phaseConfig: Record<string, { color: string; icon: string; label: string }> = {
  running: { color: "bg-green-500", icon: "🟢", label: "Running" },
  draining: { color: "bg-yellow-500", icon: "⏳", label: "Draining" },
  cleanup: { color: "bg-blue-500", icon: "🧹", label: "Cleanup" },
  terminated: { color: "bg-gray-500", icon: "⏹", label: "Terminated" },
  force_killed: { color: "bg-red-500", icon: "💀", label: "Force Killed" },
};

export function GracefulShutdownPanel({
  state,
  onShutdown,
  onForceKill,
}: {
  state: ShutdownState | null;
  onShutdown?: () => void;
  onForceKill?: () => void;
}) {
  const phases = ["running", "draining", "cleanup", "terminated"];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🛑 Shutdown</h2>
        <div className="flex gap-1">
          <button onClick={onShutdown} className="text-xs bg-yellow-600 text-white px-3 py-1 rounded-lg">Graceful</button>
          <button onClick={onForceKill} className="text-xs bg-red-600 text-white px-3 py-1 rounded-lg">Force Kill</button>
        </div>
      </div>

      {state && (
        <>
          <div className="flex gap-0.5">
            {phases.map((p) => {
              const cfg = phaseConfig[p];
              const idx = phases.indexOf(p);
              const currentIdx = phases.indexOf(state.phase);
              const isPast = idx < currentIdx;
              const isCurrent = p === state.phase;
              return (
                <div key={p} className={`flex-1 h-2 rounded-full ${isCurrent ? cfg.color + " animate-pulse" : isPast ? cfg.color : "bg-gray-200 dark:bg-gray-700"}`} />
              );
            })}
          </div>

          <div className="flex items-center gap-2">
            <span>{phaseConfig[state.phase]?.icon}</span>
            <span className="font-semibold capitalize">{phaseConfig[state.phase]?.label}</span>
            <span className="text-xs text-gray-400">{state.durationMs}ms</span>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center text-xs">
            <div className="rounded-lg border dark:border-gray-700 p-2">
              <span className="text-gray-500 block">Hooks</span>
              <span className="font-bold">{state.hooksExecuted}</span>
              {state.hooksFailed > 0 && <span className="text-red-500 ml-1">({state.hooksFailed} failed)</span>}
            </div>
            <div className="rounded-lg border dark:border-gray-700 p-2">
              <span className="text-gray-500 block">Cleaned</span>
              <span className="font-bold">{state.resourcesCleaned.length}</span>
            </div>
            <div className="rounded-lg border dark:border-gray-700 p-2">
              <span className="text-gray-500 block">Duration</span>
              <span className="font-bold">{state.durationMs}ms</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
