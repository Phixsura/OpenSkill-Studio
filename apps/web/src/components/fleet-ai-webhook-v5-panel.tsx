"use client";
export function FleetAiWebhookV5Panel({ systems, active, endpoints, delivered, failed, rate }: { systems: number; active: number; endpoints: number; delivered: number; failed: number; rate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 AI Webhook v5</h3>
    <div className="text-sm">{active}/{systems} active · {endpoints} endpoints · {delivered.toLocaleString()} delivered · {rate}%</div>
  </div>);
}
