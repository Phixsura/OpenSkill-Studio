"use client";
export function FleetAiPlayV3Panel({ playgrounds, active, sessions, collaborators, notebooks }: { playgrounds: number; active: number; sessions: number; collaborators: number; notebooks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 AI Playground v3</h3>
    <div className="text-sm">{active}/{playgrounds} active · {sessions.toLocaleString()} sessions · {collaborators} collaborators · {notebooks} notebooks</div>
  </div>);
}
