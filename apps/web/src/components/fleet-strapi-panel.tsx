"use client";
export function FleetStrapiPanel({ instances, running, contentTypes, entries }: { instances: number; running: number; contentTypes: number; entries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Strapi</h3>
    <div className="text-sm">{running}/{instances} running · {contentTypes} types · {entries.toLocaleString()} entries</div>
  </div>);
}
