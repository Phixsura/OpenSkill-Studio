"use client";
export function FleetAiPlayV2Panel({ playgrounds, active, sessions, shared, satisfaction }: { playgrounds: number; active: number; sessions: number; shared: number; satisfaction: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 AI Playground v2</h3>
    <div className="text-sm">{active}/{playgrounds} active · {sessions.toLocaleString()} sessions · {shared.toLocaleString()} shared · ⭐ {satisfaction}</div>
  </div>);
}
