"use client";
export function FleetAiAbTestPanel({ tests, running, concluded, impressions, winners }: { tests: number; running: number; concluded: number; impressions: number; winners: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 AI A/B Testing</h3>
    <div className="text-sm">{running} running · {concluded} concluded · {impressions.toLocaleString()} impressions · {winners} winners</div>
  </div>);
}
