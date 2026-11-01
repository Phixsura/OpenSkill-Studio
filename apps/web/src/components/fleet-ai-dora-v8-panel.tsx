"use client";
export function FleetAiDoraV8Panel({ freq, lead, fail, mttr, cls }: { freq: number; lead: number; fail: number; mttr: number; cls: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏆 DORA v8</h3>
    <div className="text-sm">Deploy {freq}/day · Lead {lead}m · Fail {fail}% · MTTR {mttr}m · {cls}</div>
  </div>);
}
