"use client";
export function FleetWebhookRelayV9Panel({ endpoints, delivered }: { endpoints: number; delivered: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪝 Webhook Relay v9</h3>
    <div className="text-sm">{endpoints} endpoints · {delivered.toLocaleString()} delivered</div>
  </div>);
}
