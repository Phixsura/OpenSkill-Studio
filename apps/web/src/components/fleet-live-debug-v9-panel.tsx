"use client";
export function FleetLiveDebugV9Panel({ sessions, breakpoints }: { sessions: number; breakpoints: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐛 Live Debug v9</h3>
    <div className="text-sm">{sessions} sessions · {breakpoints} breakpoints</div>
  </div>);
}
