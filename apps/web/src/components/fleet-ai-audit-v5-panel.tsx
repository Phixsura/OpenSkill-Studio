"use client";
export function FleetAiAuditV5Panel({ auditors, active, events, retention, tamperProof }: { auditors: number; active: number; events: number; retention: number; tamperProof: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 AI Audit v5</h3>
    <div className="text-sm">{active}/{auditors} active · {events.toLocaleString()} events · {retention}d retention · {tamperProof ? "✅ tamper-proof" : "⚠️"}</div>
  </div>);
}
