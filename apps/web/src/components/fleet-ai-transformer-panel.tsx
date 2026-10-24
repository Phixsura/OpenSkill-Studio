"use client";
export function FleetAiTransformerPanel({ engines, active, models, speedup, memorySaved }: { engines: number; active: number; models: number; speedup: number; memorySaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Transformer Engine</h3>
    <div className="text-sm">{active}/{engines} active · {models} models · {speedup}x speed · {memorySaved}% memory saved</div>
  </div>);
}
