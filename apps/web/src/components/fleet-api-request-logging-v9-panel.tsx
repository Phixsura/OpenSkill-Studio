"use client";
export function FleetApiRequestLoggingV9Panel({ loggers, entries }: { loggers: number; entries: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Request Logging v9</h3>
    <div className="text-sm">{loggers} loggers · {entries.toLocaleString()} entries</div>
  </div>);
}
