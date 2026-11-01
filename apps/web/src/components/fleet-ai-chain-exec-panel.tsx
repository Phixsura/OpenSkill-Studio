"use client";
export function FleetAiChainExecPanel({ executors, active, chains, steps, latency }: { executors: number; active: number; chains: number; steps: number; latency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⛓️ AI Chain Executor</h3>
    <div className="text-sm">{active}/{executors} active · {chains.toLocaleString()} chains · {steps.toLocaleString()} steps · {latency}ms</div>
  </div>);
}
