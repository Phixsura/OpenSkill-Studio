"use client";
export function FleetAiWhDelivPanel({ systems, active, sent, delivered, failed, rate }: { systems: number; active: number; sent: number; delivered: number; failed: number; rate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📨 AI Webhook Delivery</h3>
    <div className="text-sm">{active}/{systems} active · {sent.toLocaleString()} sent · {rate}% delivered · {failed} failed</div>
  </div>);
}
