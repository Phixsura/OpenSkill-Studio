"use client";

import { useState } from "react";

interface WebhookTestResult {
  statusCode: number;
  responseTime: number;
  responseBody: string;
  success: boolean;
  timestamp: string;
}

export function WebhookTesterPanel({
  extensionName,
  webhookUrl,
  onTest,
}: {
  extensionName: string;
  webhookUrl?: string;
  onTest?: (url: string, eventType: string, payload: string) => void;
}) {
  const [url, setUrl] = useState(webhookUrl || "");
  const [eventType, setEventType] = useState("extension.installed");
  const [payload, setPayload] = useState('{\n  "extension_id": "ext-1",\n  "org_id": "org-1"\n}');
  const [results, setResults] = useState<WebhookTestResult[]>([]);
  const [testing, setTesting] = useState(false);

  const eventTypes = [
    "extension.installed", "extension.published", "extension.updated",
    "review.created", "billing.subscribed", "config.changed",
  ];

  const handleTest = () => {
    setTesting(true);
    onTest?.(url, eventType, payload);
    // Simulate result
    setTimeout(() => {
      setResults((prev) => [{
        statusCode: 200, responseTime: Math.floor(Math.random() * 200 + 50),
        responseBody: '{"received": true}', success: true,
        timestamp: new Date().toLocaleTimeString(),
      }, ...prev].slice(0, 10));
      setTesting(false);
    }, 300);
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 border-b dark:border-gray-700">
        <h2 className="font-bold">🧪 Webhook Tester — {extensionName}</h2>
      </div>

      <div className="p-4 space-y-3">
        <div>
          <label className="block text-xs font-medium mb-1">Webhook URL</label>
          <input type="url" value={url} onChange={(e) => setUrl(e.target.value)}
            placeholder="https://your-server.com/webhook"
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-mono" />
        </div>

        <div>
          <label className="block text-xs font-medium mb-1">Event Type</label>
          <select value={eventType} onChange={(e) => setEventType(e.target.value)}
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm">
            {eventTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium mb-1">Payload (JSON)</label>
          <textarea value={payload} onChange={(e) => setPayload(e.target.value)}
            rows={4} className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-mono" />
        </div>

        <button onClick={handleTest} disabled={!url || testing}
          className="w-full rounded-lg bg-blue-600 text-white py-2 text-sm font-medium disabled:opacity-50">
          {testing ? "Sending..." : "🚀 Send Test Webhook"}
        </button>
      </div>

      {results.length > 0 && (
        <div className="border-t dark:border-gray-700 p-4">
          <h3 className="text-sm font-semibold mb-2">Results</h3>
          <div className="space-y-2">
            {results.map((r, i) => (
              <div key={i} className={`rounded-lg p-2 text-xs ${
                r.success ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"
              }`}>
                <div className="flex justify-between">
                  <span>{r.success ? "✅" : "❌"} {r.statusCode} · {r.responseTime}ms</span>
                  <span className="text-gray-400">{r.timestamp}</span>
                </div>
                <pre className="mt-1 text-gray-500 font-mono">{r.responseBody}</pre>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
