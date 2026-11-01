"use client";
export function FleetMultiCloudV9Panel({ providers, instances }: { providers: number; instances: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Multi-Cloud v9</h3>
    <div className="text-sm">{providers} providers · {instances} instances</div>
  </div>);
}
