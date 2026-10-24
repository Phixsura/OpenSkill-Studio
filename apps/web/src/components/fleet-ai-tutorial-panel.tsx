"use client";
export function FleetAiTutorialPanel({ engines, active, tutorials, completions, rating }: { engines: number; active: number; tutorials: number; completions: number; rating: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 AI Tutorials</h3>
    <div className="text-sm">{active}/{engines} active · {tutorials} tutorials · {completions.toLocaleString()} completions · ⭐ {rating}</div>
  </div>);
}
