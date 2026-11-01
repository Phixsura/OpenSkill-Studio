"use client";
export function FleetGofiberPanel({ services, running, rps, goroutines }: { services: number; running: number; rps: number; goroutines: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 Go Fiber</h3>
    <div className="text-sm">{running}/{services} running · {rps.toLocaleString()} rps · {goroutines.toLocaleString()} goroutines</div>
  </div>);
}
