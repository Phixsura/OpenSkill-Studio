"use client";

interface SandboxProcess {
  pid: string;
  command: string;
  state: "running" | "paused" | "stopped" | "crashed" | "killed";
  cpuPercent: number;
  memoryMb: number;
  startedAt: string;
  exitCode?: number;
}

const stateConfig: Record<string, { color: string; icon: string }> = {
  running: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "▶" },
  paused: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⏸" },
  stopped: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "⏹" },
  crashed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "💥" },
  killed: { color: "bg-red-200 text-red-800 dark:bg-red-900/40", icon: "☠" },
};

export function SandboxProcessPanel({
  processes,
  sandboxId,
  onKill,
  onPause,
  onResume,
  onKillAll,
}: {
  processes: SandboxProcess[];
  sandboxId: string;
  onKill?: (pid: string) => void;
  onPause?: (pid: string) => void;
  onResume?: (pid: string) => void;
  onKillAll?: () => void;
}) {
  const running = processes.filter((p) => p.state === "running").length;
  const totalCpu = processes.filter((p) => p.state === "running").reduce((s, p) => s + p.cpuPercent, 0);
  const totalMem = processes.filter((p) => p.state === "running").reduce((s, p) => s + p.memoryMb, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⚙️ Processes</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">{running} running · {totalCpu.toFixed(0)}% CPU · {totalMem.toFixed(0)}MB</span>
          {running > 0 && (
            <button onClick={onKillAll} className="text-xs bg-red-600 text-white px-2 py-1 rounded">Kill All</button>
          )}
        </div>
      </div>

      <div className="space-y-1">
        {processes.map((proc) => {
          const cfg = stateConfig[proc.state];
          return (
            <div key={proc.pid} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <span>{cfg.icon}</span>
                <code className="text-xs truncate">{proc.command}</code>
                <span className={`text-xs px-1.5 py-0.5 rounded-full shrink-0 ${cfg.color}`}>{proc.state}</span>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {proc.state === "running" && (
                  <span className="text-xs text-gray-400">{proc.cpuPercent}% · {proc.memoryMb}MB</span>
                )}
                {proc.exitCode != null && <span className="text-xs text-gray-400">exit:{proc.exitCode}</span>}
                {proc.state === "running" && (
                  <>
                    <button onClick={() => onPause?.(proc.pid)} className="text-xs bg-yellow-500 text-white px-2 py-0.5 rounded">⏸</button>
                    <button onClick={() => onKill?.(proc.pid)} className="text-xs bg-red-500 text-white px-2 py-0.5 rounded">Kill</button>
                  </>
                )}
                {proc.state === "paused" && (
                  <button onClick={() => onResume?.(proc.pid)} className="text-xs bg-green-500 text-white px-2 py-0.5 rounded">▶</button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
