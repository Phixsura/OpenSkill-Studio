"use client";
import { useState } from "react";

interface WebhookTestResult { valid: boolean; reason?: string; timestamp?: number; }
interface WebhookTestConsoleProps { onTest: (url: string, payload: string) => void;
  result: WebhookTestResult | null; }

export function WebhookTestConsole({ onTest, result }: WebhookTestConsoleProps) {
  const [url, setUrl] = useState("https://example.com/webhook");
  const [payload, setPayload] = useState('{"event": "test"}');

  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔐 Webhook Signature Test</h3>
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Endpoint URL</label>
          <input value={url} onChange={e => setUrl(e.target.value)}
            className="w-full text-sm px-3 py-1.5 border rounded font-mono dark:bg-gray-800 dark:border-gray-600" />
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Payload</label>
          <textarea value={payload} onChange={e => setPayload(e.target.value)} rows={3}
            className="w-full text-xs px-3 py-2 border rounded font-mono dark:bg-gray-800 dark:border-gray-600" />
        </div>
        <button onClick={() => onTest(url, payload)}
          className="w-full py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Send Test</button>
        {result && (
          <div className={`p-3 rounded-lg text-sm ${result.valid
            ? "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400"
            : "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400"}`}>
            {result.valid ? "✅ Signature verified" : `❌ Failed: ${result.reason}`}
          </div>
        )}
      </div>
    </div>
  );
}
