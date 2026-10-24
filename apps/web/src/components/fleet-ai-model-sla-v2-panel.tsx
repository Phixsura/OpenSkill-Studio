"use client";
export function FleetAiModelSlaV2Panel({ slas, active, models, met, breached }: { slas: number; active: number; models: number; met: number; breached: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Model SLA v2</h3>
    <div className="text-sm">{active}/{slas} active · {met}/{models} met · {breached} breached</div>
  </div>);
}
