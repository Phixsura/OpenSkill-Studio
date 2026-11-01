"use client";
export function FleetPanelVizPanel({ apps, running, widgets, sessions }: { apps: number; running: number; widgets: number; sessions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Panel</h3>
    <div className="text-sm">{running}/{apps} running · {widgets} widgets · {sessions.toLocaleString()} sessions</div>
  </div>);
}
