"use client";
export function FleetLabelstudioPanel({ instances, running, projects, annotations }: { instances: number; running: number; projects: number; annotations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ Label Studio</h3>
    <div className="text-sm">{running}/{instances} running · {projects} projects · {annotations.toLocaleString()} annotations</div>
  </div>);
}
