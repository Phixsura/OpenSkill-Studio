"use client";
export function FleetAiPlaygroundPanel({ playgrounds, active, users, experiments, models }: { playgrounds: number; active: number; users: number; experiments: number; models: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 AI Playground</h3>
    <div className="text-sm">{active}/{playgrounds} active · {users.toLocaleString()} users · {experiments.toLocaleString()} experiments · {models} models</div>
  </div>);
}
