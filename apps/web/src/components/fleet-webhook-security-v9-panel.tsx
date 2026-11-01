"use client";
export function FleetWebhookSecurityV9Panel({ endpoints, signed }: { endpoints: number; signed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Webhook Security v9</h3>
    <div className="text-sm">{endpoints} endpoints · {signed} HMAC signed</div>
  </div>);
}
