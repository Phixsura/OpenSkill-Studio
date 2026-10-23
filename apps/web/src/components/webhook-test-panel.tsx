"use client";

import { useState } from "react";

interface WebhookTestPanelProps { secret: string; onTest: (event: string, url: string) => void; }

const events = ["app.installed", "app.updated", "app.deleted", "review.created", "deploy.completed"];

export function WebhookTestPanel({ secret, onTest }: WebhookTestPanelProps) {
  const [event, setEvent] = useState(events[0]);
  const [url, setUrl] = useState("");

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Test Webhook</h3>
      <div className="space-y-2">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Event</label>
          <select value={event} onChange={e => setEvent(e.target.value)}
            className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600">
            {events.map(e => <option key={e}>{e}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Endpoint URL</label>
          <input type="url" value={url} onChange={e => setUrl(e.target.value)}
            placeholder="https://your-app.com/webhook"
            className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Secret</label>
          <code className="block rounded bg-gray-100 px-3 py-2 text-xs font-mono dark:bg-gray-800">{secret.slice(0, 12)}••••••</code>
        </div>
      </div>
      <button onClick={() => url && onTest(event, url)}
        className="w-full rounded bg-blue-600 py-2 text-sm text-white">Send Test Event</button>
    </div>
  );
}
