"use client";
export function FleetServiceOwnerV9Panel({ services, withOwner }: { services: number; withOwner: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👤 Service Owner v9</h3>
    <div className="text-sm">{services} services · {withOwner} with owner</div>
  </div>);
}
