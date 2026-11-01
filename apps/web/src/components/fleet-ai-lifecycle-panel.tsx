"use client";
export function FleetAiLifecyclePanel({ managers, active, models, stages }: { managers: number; active: number; models: number; stages: Record<string, number>; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Model Lifecycle</h3>
    <div className="text-sm">{active}/{managers} active · {models} models · dev {stages.dev} · prod {stages.production}</div>
  </div>);
}
