"use client";

interface Pulse { service: string; healthy: boolean; latencyMs: number; }
interface HealthPulseMonitorProps { pulses: Pulse[]; healthPct: number;
  allHealthy: boolean; improving: boolean | null; }

export function HealthPulseMonitor({ pulses, healthPct, allHealthy, improving }: HealthPulseMonitorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💓 Health Pulse</h3>
        <div className="flex gap-2 text-xs">
          <span className={allHealthy ? "text-green-600" : "text-yellow-600"}>{healthPct}%</span>
          {improving !== null && <span className={improving ? "text-green-600" : "text-red-500"}>{improving ? "↑" : "↓"}</span>}
        </div>
      </div>
      <div className="flex gap-1 p-3 flex-wrap">
        {pulses.map(p => (
          <div key={p.service} title={`${p.service}: ${p.latencyMs}ms`}
            className={`w-4 h-4 rounded ${p.healthy ? "bg-green-500" : "bg-red-500"}`} />
        ))}
      </div>
    </div>
  );
}
