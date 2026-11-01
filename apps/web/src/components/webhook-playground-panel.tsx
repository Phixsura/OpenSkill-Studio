"use client";

import { useState } from "react";

interface WebhookPlaygroundPanelProps { testEndpointUrl: string; receivedCount: number; onSendTest: (eventType: string) => void; }

const EVENT_TYPES = ["app.installed", "app.updated", "review.created", "webhook.test"];

export function WebhookPlaygroundPanel({ testEndpointUrl, receivedCount, onSendTest }: WebhookPlaygroundPanelProps) {
  const [eventType, setEventType] = useState(EVENT_TYPES[0]);

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Webhook Playground</h3>
      <div className="mt-3 rounded bg-gray-50 p-3 dark:bg-gray-800">
        <p className="text-xs text-gray-400">Test Endpoint</p>
        <code className="text-sm font-medium">{testEndpointUrl}</code>
        <p className="mt-1 text-xs text-gray-400">{receivedCount} webhooks received</p>
      </div>
      <div className="mt-3 flex gap-2">
        <select value={eventType} onChange={e => setEventType(e.target.value)}
          className="flex-1 rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700">
          {EVENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <button onClick={() => onSendTest(eventType)} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">
          Send Test
        </button>
      </div>
    </div>
  );
}
