"use client";
export function FleetMicronautPanel({ services, running, graalvm, avgMemory }: { services: number; running: number; graalvm: number; avgMemory: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 Micronaut</h3>
    <div className="text-sm">{running}/{services} running · {graalvm} GraalVM · {avgMemory}MB avg</div>
  </div>);
}
