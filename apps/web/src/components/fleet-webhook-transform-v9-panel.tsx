"use client";
export function FleetWebhookTransformV9Panel({ transforms, errors }: { transforms: number; errors: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪝 Webhook Transform v9</h3>
    <div className="text-sm">{transforms} transforms · {errors} errors</div>
  </div>);
}
