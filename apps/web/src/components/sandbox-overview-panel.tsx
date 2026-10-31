"use client";

interface SandboxInfo {
  sandboxId: string;
  extensionId: string;
  runtime: string;
  state: "created" | "running" | "stopped" | "destroyed";
  cpuPercent: number;
  memoryMb: number;
  processCount: number;
  timerCount: number;
  kvEntries: number;
  networkRequests: number;
  uptime: string;
}

const stateConfig: Record<string, { color: string; icon: string }> = {
  created: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "🆕" },
  running: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "🟢" },
  stopped: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "🔴" },
  destroyed: { color: "bg-gray-200 text-gray-500 dark:bg-gray-800", icon: "💀" },
};

export function SandboxOverviewPanel({
  sandbox,
  onStart,
  onStop,
  onDestroy,
}: {
  sandbox: SandboxInfo;
  onStart?: () => void;
  onStop?: () => void;
  onDestroy?: () => void;
}) {
  const cfg = stateConfig[sandbox.state];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold">📦 Sandbox</h2>
          <code className="text-sm text-gray-500">{sandbox.sandboxId}</code>
          <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{cfg.icon} {sandbox.state}</span>
        </div>
        <div className="flex gap-1">
          {sandbox.state === "stopped" && <button onClick={onStart} className="text-xs bg-green-600 text-white px-2 py-1 rounded">Start</button>}
          {sandbox.state === "running" && <button onClick={onStop} className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Stop</button>}
          {sandbox.state !== "destroyed" && <button onClick={onDestroy} className="text-xs bg-red-600 text-white px-2 py-1 rounded">Destroy</button>}
        </div>
      </div>

      <div className="flex gap-2 text-xs text-gray-500">
        <span>Runtime: <code className="font-bold">{sandbox.runtime}</code></span>
        <span>Extension: <code>{sandbox.extensionId}</code></span>
        {sandbox.state === "running" && <span>Uptime: {sandbox.uptime}</span>}
      </div>

      <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
        {[
          { label: "CPU", value: `${sandbox.cpuPercent}%`, warn: sandbox.cpuPercent > 80 },
          { label: "Memory", value: `${sandbox.memoryMb}MB`, warn: sandbox.memoryMb > 200 },
          { label: "Processes", value: sandbox.processCount, warn: false },
          { label: "Timers", value: sandbox.timerCount, warn: false },
          { label: "KV Keys", value: sandbox.kvEntries, warn: false },
          { label: "HTTP Reqs", value: sandbox.networkRequests, warn: false },
        ].map((m) => (
          <div key={m.label} className="rounded-lg border dark:border-gray-700 p-2 text-center">
            <span className="text-xs text-gray-400 block">{m.label}</span>
            <span className={`text-sm font-bold ${m.warn ? "text-red-600" : ""}`}>{m.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
