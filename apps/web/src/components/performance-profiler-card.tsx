"use client";

interface Hotspot { name: string; duration_ms: number; type: string; }
interface PerformanceProfilerCardProps { totalMs: number; hotspots: Hotspot[]; suggestions: string[]; }

export function PerformanceProfilerCard({ totalMs, hotspots, suggestions }: PerformanceProfilerCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Performance Profile</h3>
        <span className={`text-sm font-bold ${totalMs > 1000 ? "text-red-600" : "text-green-600"}`}>{totalMs}ms</span>
      </div>
      {hotspots.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-medium text-gray-500">Hotspots</p>
          {hotspots.map(h => (
            <div key={h.name} className="mt-1 flex items-center gap-2 text-sm">
              <div className="h-2 rounded bg-red-400" style={{ width: `${Math.max(10, (h.duration_ms / totalMs) * 100)}%` }} />
              <span className="text-xs">{h.name} ({h.duration_ms}ms)</span>
            </div>
          ))}
        </div>
      )}
      {suggestions.length > 0 && (
        <ul className="mt-3 space-y-1">
          {suggestions.map((s, i) => <li key={i} className="text-xs text-gray-500">💡 {s}</li>)}
        </ul>
      )}
    </div>
  );
}
