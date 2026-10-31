"use client";
export function FleetApiRequestLogV9Panel({ loggers, eps }: { loggers: number; eps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 API Request Log v9</h3>
    <div className="text-sm">{loggers} loggers · {eps.toLocaleString()} entries/s</div>
  </div>);
}
