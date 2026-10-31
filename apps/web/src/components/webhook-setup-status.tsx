"use client";

interface WebhookSetupStatusProps { configured: boolean; secretSet: boolean; subscriptionCount: number; setupComplete: boolean; }

export function WebhookSetupStatus({ configured, secretSet, subscriptionCount, setupComplete }: WebhookSetupStatusProps) {
  const checks = [
    { label: "Webhook URL configured", done: configured },
    { label: "Signing secret set", done: secretSet },
    { label: "Event subscriptions added", done: subscriptionCount > 0 },
  ];
  return (
    <div className={`rounded-lg border p-4 ${setupComplete ? "border-green-200 dark:border-green-800" : "border-yellow-200 dark:border-yellow-800"}`}>
      <h4 className="mb-2 font-semibold">{setupComplete ? "✅ Webhook Ready" : "⚙️ Webhook Setup"}</h4>
      <ul className="space-y-1">
        {checks.map(c => <li key={c.label} className="text-sm">{c.done ? "✅" : "⬜"} {c.label}</li>)}
      </ul>
      {subscriptionCount > 0 && <p className="mt-2 text-xs text-gray-500">{subscriptionCount} event{subscriptionCount !== 1 ? "s" : ""} subscribed</p>}
    </div>
  );
}
