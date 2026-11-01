"use client";
export function FleetBentomlPanel({ services, running, bentos, requests }: { services: number; running: number; bentos: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🍱 BentoML</h3>
    <div className="text-sm">{running}/{services} running · {bentos} bentos · {requests.toLocaleString()} req</div>
  </div>);
}
