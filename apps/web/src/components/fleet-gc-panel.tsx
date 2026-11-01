"use client";
export function FleetGcPanel({ avgPause, highPressure }: { avgPause: number; highPressure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">♻️ Fleet GC Pressure</h3>
    <div className="text-sm">Avg pause: {avgPause}ms</div>
    {highPressure && <span className="text-xs text-red-500">⚠️ High GC pressure</span>}
  </div>);
}
