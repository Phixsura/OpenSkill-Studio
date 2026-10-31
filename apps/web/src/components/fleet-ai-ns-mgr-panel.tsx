"use client";
export function FleetAiNsMgrPanel({ managers, active, namespaces, resources, conflicts }: { managers: number; active: number; namespaces: number; resources: number; conflicts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📂 AI Namespace Manager</h3>
    <div className="text-sm">{active}/{managers} active · {namespaces} namespaces · {resources.toLocaleString()} resources · {conflicts} conflicts</div>
  </div>);
}
