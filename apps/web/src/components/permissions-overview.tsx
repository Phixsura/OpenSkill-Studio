"use client";

interface PermissionsOverviewProps { read: string[]; write: string[]; special: string[]; total: number; }

export function PermissionsOverview({ read, write, special, total }: PermissionsOverviewProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-3 font-semibold">🔑 Permissions ({total})</h4>
      {read.length > 0 && <div className="mb-2"><span className="text-xs font-medium text-green-600">Read ({read.length})</span>
        <div className="mt-1 flex flex-wrap gap-1">{read.map(p => <code key={p} className="rounded bg-green-50 px-1.5 py-0.5 text-xs dark:bg-green-900/20">{p}</code>)}</div></div>}
      {write.length > 0 && <div className="mb-2"><span className="text-xs font-medium text-yellow-600">Write ({write.length})</span>
        <div className="mt-1 flex flex-wrap gap-1">{write.map(p => <code key={p} className="rounded bg-yellow-50 px-1.5 py-0.5 text-xs dark:bg-yellow-900/20">{p}</code>)}</div></div>}
      {special.length > 0 && <div><span className="text-xs font-medium text-purple-600">Special ({special.length})</span>
        <div className="mt-1 flex flex-wrap gap-1">{special.map(p => <code key={p} className="rounded bg-purple-50 px-1.5 py-0.5 text-xs dark:bg-purple-900/20">{p}</code>)}</div></div>}
    </div>
  );
}
