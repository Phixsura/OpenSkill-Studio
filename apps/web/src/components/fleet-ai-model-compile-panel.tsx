"use client";
export function FleetAiModelCompilePanel({ compilers, active, models, speedup, targets }: { compilers: number; active: number; models: number; speedup: number; targets: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ AI Model Compiler</h3>
    <div className="text-sm">{active}/{compilers} active · {models} models · {speedup}x speed · {targets} targets</div>
  </div>);
}
