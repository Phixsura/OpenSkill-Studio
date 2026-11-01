"use client";
export function FleetAiPromptsPanel({ registries, prompts, versions, evaluations }: { registries: number; prompts: number; versions: number; evaluations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💬 AI Prompts</h3>
    <div className="text-sm">{registries} registries · {prompts} prompts · {versions} versions · {evaluations.toLocaleString()} evals</div>
  </div>);
}
