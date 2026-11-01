"use client";
export function FleetNetworkMonitorV9Panel({ interfaces, errors }: { interfaces: number; errors: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 Network Monitor v9</h3>
    <div className="text-sm">{interfaces} interfaces · {errors} errors</div>
  </div>);
}
