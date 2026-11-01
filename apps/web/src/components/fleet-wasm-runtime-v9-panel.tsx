"use client";
export function FleetWasmRuntimeV9Panel({ modules, invocations }: { modules: number; invocations: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ WASM Runtime v9</h3>
    <div className="text-sm">{modules} modules · {invocations.toLocaleString()} invocations</div>
  </div>);
}
