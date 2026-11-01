"use client";
export function FleetAiPlaySbPanel({ sandboxes, active, sessions, duration, models }: { sandboxes: number; active: number; sessions: number; duration: number; models: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 AI Playground Sandbox</h3>
    <div className="text-sm">{active}/{sandboxes} active · {sessions.toLocaleString()} sessions · {duration}m avg · {models} models</div>
  </div>);
}
