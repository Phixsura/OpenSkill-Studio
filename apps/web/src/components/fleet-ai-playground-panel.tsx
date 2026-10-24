"use client";
export function FleetAiPlaygroundPanel({ instances, active, sessions, prompts }: { instances: number; active: number; sessions: number; prompts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 AI Playground</h3>
    <div className="text-sm">{active}/{instances} active · {sessions.toLocaleString()} sessions · {prompts.toLocaleString()} prompts</div>
  </div>);
}
