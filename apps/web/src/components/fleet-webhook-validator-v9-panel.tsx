"use client";
export function FleetWebhookValidatorV9Panel({ endpoints, validated }: { endpoints: number; validated: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪝 Webhook Validator v9</h3>
    <div className="text-sm">{endpoints} endpoints · {validated.toLocaleString()} validated</div>
  </div>);
}
