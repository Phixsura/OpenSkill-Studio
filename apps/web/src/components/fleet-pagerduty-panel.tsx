"use client";
export function FleetPagerdutyPanel({ services, activeIncidents, acknowledged, avgAck }: { services: number; activeIncidents: number; acknowledged: number; avgAck: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📟 PagerDuty</h3>
    <div className="text-sm">{services} services · {activeIncidents} active · {avgAck}min avg ack</div>
  </div>);
}
