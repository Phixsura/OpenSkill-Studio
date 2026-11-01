"use client";
export function FleetAiSandboxPanel({ sandboxes, running, executions, isolated }: { sandboxes: number; running: number; executions: number; isolated: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏖️ AI Sandbox</h3>
    <div className="text-sm">{running}/{sandboxes} running · {executions.toLocaleString()} exec · {isolated} isolated</div>
  </div>);
}
