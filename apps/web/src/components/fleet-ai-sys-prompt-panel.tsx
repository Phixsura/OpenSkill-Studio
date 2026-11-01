"use client";
export function FleetAiSysPromptPanel({ managers, active, prompts, versions, uses }: { managers: number; active: number; prompts: number; versions: number; uses: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 AI System Prompt</h3>
    <div className="text-sm">{active}/{managers} active · {prompts} prompts · {versions} versions · {uses.toLocaleString()} uses</div>
  </div>);
}
