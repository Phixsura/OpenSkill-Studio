"use client";
export function FleetWebhookRetryV9Panel({ queues, deadLetter }: { queues: number; deadLetter: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔁 Webhook Retry v9</h3>
    <div className="text-sm">{queues} queues · {deadLetter} dead letter</div>
  </div>);
}
