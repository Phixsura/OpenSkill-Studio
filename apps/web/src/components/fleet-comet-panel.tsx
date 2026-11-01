"use client";
export function FleetCometPanel({ workspaces, active, experiments, panels }: { workspaces: number; active: number; experiments: number; panels: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☄️ Comet</h3>
    <div className="text-sm">{active}/{workspaces} active · {experiments.toLocaleString()} experiments · {panels} panels</div>
  </div>);
}
