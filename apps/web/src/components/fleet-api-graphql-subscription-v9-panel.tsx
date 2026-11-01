"use client";
export function FleetApiGraphqlSubscriptionV9Panel({ subs, connections }: { subs: number; connections: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">◈ GraphQL Sub v9</h3>
    <div className="text-sm">{subs} subs · {connections.toLocaleString()} connections</div>
  </div>);
}
