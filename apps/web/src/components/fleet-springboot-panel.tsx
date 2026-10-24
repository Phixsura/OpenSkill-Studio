"use client";
export function FleetSpringbootPanel({ services, up, beans, heapPct }: { services: number; up: number; beans: number; heapPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🍃 Spring Boot</h3>
    <div className="text-sm">{up}/{services} UP · {beans} beans · {heapPct}% heap</div>
  </div>);
}
