"use client";
export function FleetAiAuditV8Panel({ auditors, active, events, retention, tamperProof }: { auditors: number; active: number; events: number; retention: number; tamperProof: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 AI Audit v8</h3>
    <div className="text-sm">{active}/{auditors} active · {events.toLocaleString()} events · {retention}d · {tamperProof ? "✅ tamper-proof" : "⚠️"}</div>
  </div>);
}
