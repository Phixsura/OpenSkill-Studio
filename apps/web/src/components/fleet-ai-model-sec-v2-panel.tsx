"use client";
export function FleetAiModelSecV2Panel({ systems, active, models, threats, encrypted }: { systems: number; active: number; models: number; threats: number; encrypted: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Model Security v2</h3>
    <div className="text-sm">{active}/{systems} active · {models} models · {threats} threats blocked · {encrypted}% encrypted</div>
  </div>);
}
