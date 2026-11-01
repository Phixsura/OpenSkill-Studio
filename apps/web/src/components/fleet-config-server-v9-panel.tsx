"use client";
export function FleetConfigServerV9Panel({ configs, watchers }: { configs: number; watchers: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ Config Server v9</h3>
    <div className="text-sm">{configs} configs · {watchers} watchers</div>
  </div>);
}
