"use client";
export function FleetAiIntentPanel({ services, active, classifications, intents }: { services: number; active: number; classifications: number; intents: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI Intent</h3>
    <div className="text-sm">{active}/{services} active · {classifications.toLocaleString()} classified · {intents} intents</div>
  </div>);
}
