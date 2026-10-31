"use client";
export function FleetAiGraceShutPanel({ managers, active, shutdowns, drained, lost }: { managers: number; active: number; shutdowns: number; drained: number; lost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛑 AI Graceful Shutdown</h3>
    <div className="text-sm">{active}/{managers} active · {shutdowns} shutdowns · {drained.toLocaleString()} drained · {lost} lost</div>
  </div>);
}
