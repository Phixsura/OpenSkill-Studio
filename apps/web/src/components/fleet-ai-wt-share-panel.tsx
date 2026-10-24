"use client";
export function FleetAiWtSharePanel({ configs, active, sharedLayers, savedGb, models }: { configs: number; active: number; sharedLayers: number; savedGb: number; models: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 AI Weight Sharing</h3>
    <div className="text-sm">{active}/{configs} active · {sharedLayers} layers · {savedGb}GB saved · {models} models</div>
  </div>);
}
