"use client";

interface VersionStatusSummaryProps { total: number; approved: number; pending: number; rejected: number; latestVersion: string | null; hasPending: boolean; }

export function VersionStatusSummary({ total, approved, pending, rejected, latestVersion, hasPending }: VersionStatusSummaryProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-2 flex items-center justify-between">
        <h4 className="font-semibold">📦 Versions</h4>
        {latestVersion && <span className="font-mono text-sm">Latest: v{latestVersion}</span>}
      </div>
      <div className="grid grid-cols-4 gap-2 text-center text-sm">
        <div><p className="text-lg font-bold">{total}</p><p className="text-xs text-gray-500">Total</p></div>
        <div><p className="text-lg font-bold text-green-600">{approved}</p><p className="text-xs text-gray-500">Approved</p></div>
        <div><p className="text-lg font-bold text-yellow-600">{pending}</p><p className="text-xs text-gray-500">Pending</p></div>
        <div><p className="text-lg font-bold text-red-600">{rejected}</p><p className="text-xs text-gray-500">Rejected</p></div>
      </div>
      {hasPending && <p className="mt-2 text-xs text-yellow-600">⏳ Review in progress — cannot create new version</p>}
    </div>
  );
}
