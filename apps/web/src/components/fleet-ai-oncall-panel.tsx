"use client";
export function FleetAiOncallPanel({ schedulers, active, engineers, pages, ackMin }: { schedulers: number; active: number; engineers: number; pages: number; ackMin: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📟 AI On-Call</h3>
    <div className="text-sm">{active}/{schedulers} active · {engineers} engineers · {pages} pages · {ackMin}m ack</div>
  </div>);
}
