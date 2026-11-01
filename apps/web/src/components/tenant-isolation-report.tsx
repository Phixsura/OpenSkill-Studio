"use client";

interface Violation { resource: string; owner: string; accessedBy: string; severity: string; }
interface TenantIsolationReportProps { status: string; summary: string;
  verdict: string; violations: Violation[]; }

export function TenantIsolationReport({ status, summary, verdict, violations }: TenantIsolationReportProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🔐 Tenant Isolation</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          status === "secure" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
        }`}>{status}</span>
      </div>
      <p className="text-xs text-gray-400 mb-2">{summary}</p>
      <p className={`text-sm font-medium mb-3 ${status === "secure" ? "text-green-600" : "text-red-600"}`}>{verdict}</p>
      {violations.length > 0 && (
        <div className="space-y-2">
          {violations.map((v, i) => (
            <div key={i} className="bg-red-50 dark:bg-red-900/10 rounded-lg px-3 py-2 text-sm">
              <span className="font-mono text-xs">{v.resource}</span>
              <span className="text-xs text-gray-400 mx-1">owned by</span>
              <span className="font-medium">{v.owner}</span>
              <span className="text-xs text-red-500 ml-1">→ accessed by {v.accessedBy}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
