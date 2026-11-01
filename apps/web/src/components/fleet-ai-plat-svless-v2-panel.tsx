"use client";
export function FleetAiPlatSvlessV2Panel({ platforms, active, functions, invocations, coldMs }: { platforms: number; active: number; functions: number; invocations: number; coldMs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Serverless v2</h3>
    <div className="text-sm">{active}/{platforms} active · {functions} functions · {invocations.toLocaleString()} invocations · {coldMs}ms cold</div>
  </div>);
}
