"use client";
export function FleetLambdaPanel({ functions, active, invocations, errors, coldStart }: { functions: number; active: number; invocations: number; errors: number; coldStart: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">λ AWS Lambda</h3>
    <div className="text-sm">{active}/{functions} active · {invocations.toLocaleString()} inv · {coldStart}% cold</div>
    {errors > 0 && <span className="text-xs text-red-500">⚠️ {errors} errors</span>}
  </div>);
}
