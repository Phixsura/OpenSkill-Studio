"use client";

import { useState } from "react";

interface TestResult {
  test_id: string;
  event_type: string;
  webhook_url: string;
  status: "pass" | "fail" | "error" | "pending";
  status_code: number | null;
  latency_ms: number | null;
  response_body: string | null;
  error: string | null;
  timestamp: string;
}

interface WebhookTestConsoleProps {
  templates: string[];
  history: TestResult[];
  passRate: number;
  onSendTest: (eventType: string, url: string) => void;
}

const STATUS_STYLES: Record<string, { label: string; color: string }> = {
  pass: {
    label: "Pass",
    color: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300",
  },
  fail: { label: "Fail", color: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300" },
  error: {
    label: "Error",
    color: "bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-300",
  },
  pending: {
    label: "Pending",
    color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  },
};

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function WebhookTestConsole({
  templates,
  history,
  passRate,
  onSendTest,
}: WebhookTestConsoleProps) {
  const [selectedEvent, setSelectedEvent] = useState(templates[0] ?? "");
  const [webhookUrl, setWebhookUrl] = useState("");

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">Webhook Test Console</h3>
          <span
            className={`text-xs font-medium ${passRate >= 80 ? "text-green-600" : passRate >= 50 ? "text-yellow-600" : "text-red-600"}`}
          >
            {passRate}% pass rate
          </span>
        </div>
      </div>

      {/* Send form */}
      <div className="space-y-2 border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex gap-2">
          <select
            value={selectedEvent}
            onChange={(e) => setSelectedEvent(e.target.value)}
            className="flex-1 rounded border border-gray-300 px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800"
            aria-label="Event type"
          >
            {templates.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={webhookUrl}
            onChange={(e) => setWebhookUrl(e.target.value)}
            placeholder="https://your-app.com/webhook"
            className="flex-1 rounded border border-gray-300 px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800"
            aria-label="Webhook URL"
          />
          <button
            onClick={() => onSendTest(selectedEvent, webhookUrl)}
            disabled={!webhookUrl.trim()}
            className="rounded-md bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Send Test
          </button>
        </div>
      </div>

      {/* History */}
      {history.length === 0 ? (
        <div className="py-6 text-center">
          <span className="text-2xl">🧪</span>
          <p className="mt-1 text-sm text-gray-500">No tests yet — send one above</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {history.map((r) => {
            const st = STATUS_STYLES[r.status] ?? STATUS_STYLES.pending;
            return (
              <div key={r.test_id} className="px-4 py-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${st.color}`}>
                      {st.label}
                    </span>
                    <code className="text-xs">{r.event_type}</code>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] text-gray-400">
                    {r.status_code && <span>HTTP {r.status_code}</span>}
                    {r.latency_ms !== null && <span>{r.latency_ms}ms</span>}
                    <span>{formatTime(r.timestamp)}</span>
                  </div>
                </div>
                {r.error && <p className="mt-0.5 text-[10px] text-red-500">{r.error}</p>}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
