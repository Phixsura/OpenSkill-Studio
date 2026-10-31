"use client";
export function FleetAiModelHubPanel({ hubs, active, models, contributors, downloads }: { hubs: number; active: number; models: number; contributors: number; downloads: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏠 AI Model Hub</h3>
    <div className="text-sm">{active}/{hubs} active · {models} models · {contributors} contributors · {downloads.toLocaleString()} downloads</div>
  </div>);
}
