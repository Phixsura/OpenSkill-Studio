"use client";
export function FleetAiWebhookPanel({ endpoints, active, delivered, failed }: { endpoints: number; active: number; delivered: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 AI Webhooks</h3>
    <div className="text-sm">{active}/{endpoints} active · {delivered.toLocaleString()} delivered · {failed} failed</div>
  </div>);
}
