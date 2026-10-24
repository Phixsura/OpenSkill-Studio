"use client";
export function FleetAiPlatDoraV3Panel({ freq, lead, fail, mttr, trend, classification }: { freq: number; lead: number; fail: number; mttr: number; trend: string; classification: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏆 DORA v3</h3>
    <div className="text-sm">Deploy {freq}/day · Lead {lead}m · Fail {fail}% · MTTR {mttr}m · {trend} · {classification}</div>
  </div>);
}
