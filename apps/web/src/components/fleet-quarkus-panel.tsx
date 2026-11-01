"use client";
export function FleetQuarkusPanel({ services, running, native, avgStartup }: { services: number; running: number; native: number; avgStartup: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔵 Quarkus</h3>
    <div className="text-sm">{running}/{services} running · {native} native · {avgStartup}ms startup</div>
  </div>);
}
