"use client";
export function FleetMinioPanel({ servers, online, totalTb, usedTb, usagePct }: { servers: number; online: number; totalTb: number; usedTb: number; usagePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪣 MinIO</h3>
    <div className="text-sm">{online}/{servers} online · {usedTb}/{totalTb}TB ({usagePct}%)</div>
  </div>);
}
