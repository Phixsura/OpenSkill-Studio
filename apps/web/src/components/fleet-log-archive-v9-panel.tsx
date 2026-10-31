"use client";
export function FleetLogArchiveV9Panel({ archives, sizeTb }: { archives: number; sizeTb: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Log Archive v9</h3>
    <div className="text-sm">{archives} archives · {sizeTb} TB</div>
  </div>);
}
