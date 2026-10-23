"use client";

interface ChaosExperimentCardProps { name: string; target: string; faultType: string;
  durationSec: number; magnitude: number; status: string; resilient: boolean | null;
  onRun: () => void; onStop: () => void; }

const FAULT_ICONS: Record<string, string> = {
  latency: "⏳", error: "💥", timeout: "⌛", cpu_spike: "🔥",
  memory_leak: "💧", network_partition: "🔌",
};

export function ChaosExperimentCard({ name, target, faultType, durationSec, magnitude, status, resilient, onRun, onStop }: ChaosExperimentCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">{FAULT_ICONS[faultType] ?? "⚡"} {name}</h3>
          <div className="text-[10px] text-gray-400">Target: {target} · {faultType} · {durationSec}s · {magnitude}x</div>
        </div>
        <div className="flex gap-2">
          {resilient !== null && (
            <span className={`text-xs ${resilient ? "text-green-600" : "text-red-500"}`}>
              {resilient ? "✅ Resilient" : "⚠ Vulnerable"}
            </span>
          )}
          {status === "ready" ? (
            <button onClick={onRun} className="px-2 py-1 text-xs bg-red-500 text-white rounded">Run</button>
          ) : (
            <button onClick={onStop} className="px-2 py-1 text-xs bg-gray-500 text-white rounded">Stop</button>
          )}
        </div>
      </div>
    </div>
  );
}
