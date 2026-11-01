"use client";

import { useState } from "react";

interface Template { id: string; name: string; eventType: string; placeholders: number; }

export default function WebhookTemplateCard() {
  const [templates] = useState<Template[]>([
    { id: "t1", name: "Order Created", eventType: "order.created", placeholders: 4 },
    { id: "t2", name: "User Signup", eventType: "user.created", placeholders: 3 },
    { id: "t3", name: "Payment Failed", eventType: "payment.failed", placeholders: 5 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Templates</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Reusable webhook payload templates</p>

      <div className="mt-4 space-y-2">
        {templates.map((t) => (
          <div key={t.id} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{t.name}</span>
              <span className="ml-2 text-xs text-zinc-400">{t.eventType}</span>
            </div>
            <span className="text-xs text-zinc-500">{t.placeholders} vars</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{templates.length} templates</div>
    </div>
  );
}
