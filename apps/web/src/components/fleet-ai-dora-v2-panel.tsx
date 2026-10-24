"use client";
export function FleetAiDoraV2Panel({ deployFreq, leadTime, failPct, mttr, classification }: { deployFreq: number; leadTime: number; failPct: number; mttr: number; classification: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏆 DORA Metrics v2</h3>
    <div className="text-sm">Deploy {deployFreq}/day · Lead {leadTime}m · Fail {failPct}% · MTTR {mttr}m · {classification}</div>
  </div>);
}
