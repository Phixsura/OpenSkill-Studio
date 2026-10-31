"use client";
export function FleetAiAuditTrailPanel({ trails, active, events, retention, tamperProof }: { trails: number; active: number; events: number; retention: number; tamperProof: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 AI Audit Trail</h3>
    <div className="text-sm">{active}/{trails} active · {events.toLocaleString()} events · {retention}d retention · {tamperProof ? "✅" : "⚠️"} tamper-proof</div>
  </div>);
}
