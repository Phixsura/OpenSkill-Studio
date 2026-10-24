"use client";

import { useState } from "react";

interface WebhookConfigFormProps {
  initialUrl?: string;
  availableEvents: string[];
  onSave: (config: { url: string; events: string[] }) => void;
}

export function WebhookConfigForm({ initialUrl, availableEvents, onSave }: WebhookConfigFormProps) {
  const [url, setUrl] = useState(initialUrl ?? "");
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);

  const toggleEvent = (event: string) => {
    setSelectedEvents(prev => prev.includes(event) ? prev.filter(e => e !== event) : [...prev, event]);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium">Webhook URL</label>
        <input type="url" value={url} onChange={e => setUrl(e.target.value)} placeholder="https://..."
          className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800" />
      </div>
      <div>
        <label className="text-sm font-medium">Events</label>
        <div className="mt-1 flex flex-wrap gap-1">
          {availableEvents.map(event => (
            <button key={event} onClick={() => toggleEvent(event)} type="button"
              className={`rounded-full border px-2 py-0.5 text-xs ${selectedEvents.includes(event) ? "border-blue-500 bg-blue-100" : "border-gray-300"}`}>
              {event}
            </button>
          ))}
        </div>
      </div>
      <button onClick={() => onSave({ url, events: selectedEvents })} disabled={!url || selectedEvents.length === 0}
        className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50">Save Webhook</button>
    </div>
  );
}
