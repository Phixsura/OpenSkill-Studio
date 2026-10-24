"use client";
export function FleetAiPromptTplPanel({ libraries, active, templates, uses, tokensSaved }: { libraries: number; active: number; templates: number; uses: number; tokensSaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 AI Prompt Templates</h3>
    <div className="text-sm">{active}/{libraries} active · {templates} templates · {uses.toLocaleString()} uses · {tokensSaved.toLocaleString()} tokens saved</div>
  </div>);
}
