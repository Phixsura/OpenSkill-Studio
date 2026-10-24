"use client";
interface ProfileData { endpoint: string; samples: number; avg: number; p50: number; p95: number; p99: number; }
interface PerfProfilePanelProps { profiles: ProfileData[]; totalSamples: number; }
export function PerfProfilePanel({ profiles, totalSamples }: PerfProfilePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Performance Profiler</h3>
        <span className="text-xs text-gray-400">{profiles.length} endpoints · {totalSamples.toLocaleString()} samples</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {profiles.map(p => (
          <div key={p.endpoint} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{p.endpoint}</span>
            <span className="text-gray-400">avg:{p.avg}ms p95:{p.p95}ms p99:{p.p99}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
