"use client";
export function FleetPostgrestPanel({ instances, running, rps, schemas }: { instances: number; running: number; rps: number; schemas: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐘 PostgREST</h3>
    <div className="text-sm">{running}/{instances} running · {rps.toLocaleString()} rps · {schemas} schemas</div>
  </div>);
}
