"use client";
export function FleetWebhookDelPanel({ delivered, failed, successRate, reliable }: { delivered: number; failed: number; successRate: number; reliable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 Webhook Delivery</h3>
    <div className={`text-lg font-bold ${reliable ? "text-green-600" : "text-red-500"}`}>{successRate}%</div>
    <div className="text-xs text-gray-400">{delivered.toLocaleString()} delivered · {failed} failed</div>
  </div>);
}
