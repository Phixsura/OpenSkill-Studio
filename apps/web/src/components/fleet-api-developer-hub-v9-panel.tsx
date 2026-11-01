"use client";
export function FleetApiDeveloperHubV9Panel({ devs, docs }: { devs: number; docs: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 Developer Hub v9</h3>
    <div className="text-sm">{devs.toLocaleString()} devs · {docs} docs pages</div>
  </div>);
}
