"use client";
export function FleetDeepnotePanel({ workspaces, active, projects, integrations }: { workspaces: number; active: number; projects: number; integrations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Deepnote</h3>
    <div className="text-sm">{active}/{workspaces} active · {projects} projects · {integrations} integrations</div>
  </div>);
}
