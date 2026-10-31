"use client";
export function FleetAccessLogV9Panel({ sources, entries }: { sources: number; entries: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Access Log v9</h3>
    <div className="text-sm">{sources} sources · {entries.toLocaleString()} entries</div>
  </div>);
}
