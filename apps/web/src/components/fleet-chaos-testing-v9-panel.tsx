"use client";
export function FleetChaosTestingV9Panel({ services, coverage }: { services: number; coverage: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ Chaos Testing v9</h3>
    <div className="text-sm">{services} services · {coverage}% chaos coverage</div>
  </div>);
}
