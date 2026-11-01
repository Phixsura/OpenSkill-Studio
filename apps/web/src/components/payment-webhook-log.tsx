"use client";

interface PaymentEvent { event: string; amount: number; currency: string;
  customer: string; action: string; }
interface PaymentWebhookLogProps { events: PaymentEvent[]; total: number; }

const EVENT_ICONS: Record<string, string> = {
  "payment.completed": "✅", "payment.failed": "❌", "refund.created": "↩️",
  "subscription.created": "🟢", "subscription.cancelled": "🔴",
};

export function PaymentWebhookLog({ events, total }: PaymentWebhookLogProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💳 Payment Webhooks</h3>
        <span className="text-xs text-gray-400">{total} events</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {events.map((e, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span>{EVENT_ICONS[e.event] ?? "📨"}</span>
              <div>
                <span className="text-xs font-mono">{e.event}</span>
                <div className="text-[10px] text-gray-400">{e.customer} · {e.action}</div>
              </div>
            </div>
            <span className="text-xs font-mono">{(e.amount / 100).toFixed(2)} {e.currency}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
