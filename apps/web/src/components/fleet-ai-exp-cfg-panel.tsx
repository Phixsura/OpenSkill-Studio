"use client";
export function FleetAiExpCfgPanel({ managers, active, configs, templates, overrides }: { managers: number; active: number; configs: number; templates: number; overrides: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ AI Experiment Config</h3>
    <div className="text-sm">{active}/{managers} active · {configs} configs · {templates} templates · {overrides} overrides</div>
  </div>);
}
