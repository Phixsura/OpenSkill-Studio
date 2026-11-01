"use client";
export function FleetScaffolderPanel({ templates, executions, topTemplate }: { templates: number; executions: number; topTemplate: string | null; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ Scaffolder</h3>
    <div className="text-sm">{templates} templates · {executions} executions/30d</div>
    {topTemplate && <div className="text-xs text-blue-500">Top: {topTemplate}</div>}
  </div>);
}
