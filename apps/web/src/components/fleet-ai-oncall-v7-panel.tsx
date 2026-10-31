"use client";
export function FleetAiOncallV7Panel({ schedulers, active, engineers, pages, ack, auto }: { schedulers: number; active: number; engineers: number; pages: number; ack: number; auto: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📟 AI On-Call v7</h3>
    <div className="text-sm">{active}/{schedulers} active · {engineers} engineers · {pages} pages · {ack}m ack · {auto} auto</div>
  </div>);
}
