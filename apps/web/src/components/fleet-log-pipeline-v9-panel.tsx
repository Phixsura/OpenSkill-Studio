"use client";
export function FleetLogPipelineV9Panel({ rate, dropped }: { rate: number; dropped: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Log Pipeline v9</h3>
    <div className="text-sm">{rate.toLocaleString()} events/s · {dropped} dropped</div>
  </div>);
}
