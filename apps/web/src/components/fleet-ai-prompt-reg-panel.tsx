"use client";
export function FleetAiPromptRegPanel({ registries, active, templates, versions }: { registries: number; active: number; templates: number; versions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 AI Prompt Registry</h3>
    <div className="text-sm">{active}/{registries} active · {templates} templates · {versions} versions</div>
  </div>);
}
