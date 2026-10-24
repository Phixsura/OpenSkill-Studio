"use client";
export function FleetAzureFuncPanel({ apps, running, executions, gbSeconds }: { apps: number; running: number; executions: number; gbSeconds: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Azure Functions</h3>
    <div className="text-sm">{running}/{apps} running · {executions.toLocaleString()} exec · {gbSeconds.toLocaleString()} GB·s</div>
  </div>);
}
