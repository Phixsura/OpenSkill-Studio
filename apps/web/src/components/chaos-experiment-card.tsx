"use client";

interface ChaosExperimentCardProps {
  faultType: string; target: string; durationSeconds: number; status: string;
  grade?: string; onStart: () => void; onStop: () => void;
}

const FAULT_ICONS: Record<string, string> = {
  latency: "🐌", error: "💥", timeout: "⏳", connection_drop: "🔌", cpu_spike: "🔥",
};

export function ChaosExperimentCard({ faultType, target, durationSeconds, status, grade, onStart, onStop }: ChaosExperimentCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">{FAULT_ICONS[faultType] || "🧪"}</span>
          <div>
            <h3 className="font-semibold capitalize">{faultType.replace("_", " ")}</h3>
            <p className="text-xs text-gray-400">Target: {target} · {durationSeconds}s</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {grade && <span className={`text-lg font-bold ${grade === "A" ? "text-green-600" : grade === "F" ? "text-red-600" : "text-yellow-600"}`}>{grade}</span>}
          {status === "ready" ? (
            <button onClick={onStart} className="rounded bg-red-600 px-3 py-1 text-xs text-white">Start</button>
          ) : status === "running" ? (
            <button onClick={onStop} className="rounded bg-gray-600 px-3 py-1 text-xs text-white">Stop</button>
          ) : <span className="text-xs text-gray-400">{status}</span>}
        </div>
      </div>
    </div>
  );
}
