"use client";
export function FleetPostmarkPanel({ servers, active, delivered, bounceRate }: { servers: number; active: number; delivered: number; bounceRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✉️ Postmark</h3>
    <div className="text-sm">{active}/{servers} active · {delivered.toLocaleString()} delivered · {bounceRate}% bounce</div>
  </div>);
}
