"use client";
export function FleetAiPromptOptPanel({ optimizers, active, optimized, improvement, tokensSaved }: { optimizers: number; active: number; optimized: number; improvement: number; tokensSaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✨ AI Prompt Optimizer</h3>
    <div className="text-sm">{active}/{optimizers} active · {optimized.toLocaleString()} optimized · +{improvement}% · {tokensSaved.toLocaleString()} tokens saved</div>
  </div>);
}
