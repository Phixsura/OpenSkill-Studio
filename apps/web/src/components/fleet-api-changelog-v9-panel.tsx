"use client";
export function FleetApiChangelogV9Panel({ apis, entries }: { apis: number; entries: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 API Changelog v9</h3>
    <div className="text-sm">{apis} APIs · {entries} entries</div>
  </div>);
}
