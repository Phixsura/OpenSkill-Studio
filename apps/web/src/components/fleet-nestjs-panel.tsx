"use client";
export function FleetNestjsPanel({ apps, running, modules, endpoints }: { apps: number; running: number; modules: number; endpoints: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐈 NestJS</h3>
    <div className="text-sm">{running}/{apps} running · {modules} modules · {endpoints} endpoints</div>
  </div>);
}
