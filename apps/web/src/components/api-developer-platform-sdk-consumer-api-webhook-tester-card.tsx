"use client";

import { useState } from "react";

interface TestInfo { testId: string; eventType: string; success: boolean; latencyMs: number; }

export default function WebhookTesterCard() {
  const [tests] = useState<TestInfo[]>([
    { testId: "t1", eventType: "order.created", success: true, latencyMs: 45 },
    { testId: "t2", eventType: "user.signup", success: true, latencyMs: 120 },
    { testId: "t3", eventType: "payment.failed", success: false, latencyMs: 5000 },
  ]);

  const passed = tests.filter((t) => t.success).length;

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Tester</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Test webhooks with mock payloads</p>

      <div className="mt-4 space-y-2">
        {tests.map((t) => (
          <div key={t.testId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${t.success ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm text-zinc-800 dark:text-zinc-200">{t.eventType}</span>
            </div>
            <span className="text-xs text-zinc-400">{t.latencyMs}ms</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {passed}/{tests.length} tests passed
      </div>
    </div>
  );
}
