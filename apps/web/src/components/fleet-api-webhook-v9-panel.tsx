"use client";
export function FleetApiWebhookV9Panel({ webhooks, delivered }: { webhooks: number; delivered: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪝 API Webhook v9</h3>
    <div className="text-sm">{webhooks} webhooks · {delivered.toLocaleString()} delivered</div>
  </div>);
}
