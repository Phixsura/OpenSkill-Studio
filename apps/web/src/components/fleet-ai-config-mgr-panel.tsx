"use client";
export function FleetAiConfigMgrPanel({ managers, active, configs, versions, rollbacks }: { managers: number; active: number; configs: number; versions: number; rollbacks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ AI Config Manager</h3>
    <div className="text-sm">{active}/{managers} active · {configs} configs · {versions} versions · {rollbacks} rollbacks</div>
  </div>);
}
