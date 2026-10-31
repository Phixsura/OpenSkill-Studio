"use client";
export function FleetWasmPanel({ modules, loaded, executions, avgExec }: { modules: number; loaded: number; executions: number; avgExec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 WASM</h3>
    <div className="text-sm">{loaded}/{modules} loaded · {executions.toLocaleString()} exec · {avgExec}ms avg</div>
  </div>);
}
