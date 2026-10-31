"use client";
export function FleetApiSecurityAuditV9Panel({ audits, findings }: { audits: number; findings: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Security Audit v9</h3>
    <div className="text-sm">{audits} audits · {findings} findings</div>
  </div>);
}
