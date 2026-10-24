"use client";
export function FleetWebhookFilterV9Panel({ filters, passed }: { filters: number; passed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪝 Webhook Filter v9</h3>
    <div className="text-sm">{filters} filters · {passed.toLocaleString()} passed</div>
  </div>);
}
