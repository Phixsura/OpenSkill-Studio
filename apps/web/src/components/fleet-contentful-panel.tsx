"use client";
export function FleetContentfulPanel({ spaces, active, entries, apiCalls }: { spaces: number; active: number; entries: number; apiCalls: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 Contentful</h3>
    <div className="text-sm">{active}/{spaces} active · {entries.toLocaleString()} entries · {apiCalls.toLocaleString()} calls</div>
  </div>);
}
