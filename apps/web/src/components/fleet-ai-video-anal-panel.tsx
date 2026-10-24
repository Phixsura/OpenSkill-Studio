"use client";
export function FleetAiVideoAnalPanel({ analyzers, active, hours, fps, events }: { analyzers: number; active: number; hours: number; fps: number; events: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎬 AI Video Analysis</h3>
    <div className="text-sm">{active}/{analyzers} active · {hours.toLocaleString()}h · {fps} FPS · {events.toLocaleString()} events</div>
  </div>);
}
