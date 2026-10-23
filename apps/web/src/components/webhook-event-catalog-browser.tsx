"use client";

import { useState } from "react";

interface EventInfo { event: string; description: string; payload_example: Record<string, unknown>; }
interface Category { category: string; label: string; events: EventInfo[]; }
interface WebhookEventCatalogBrowserProps { categories: Category[]; totalEvents: number;
  onSubscribe: (event: string) => void; }

export function WebhookEventCatalogBrowser({ categories, totalEvents, onSubscribe }: WebhookEventCatalogBrowserProps) {
  const [expanded, setExpanded] = useState<string | null>(categories[0]?.category ?? null);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Webhook Events</h2>
        <span className="text-xs text-gray-400">{totalEvents} events available</span>
      </div>
      {categories.map(cat => (
        <div key={cat.category} className="rounded-lg border dark:border-gray-700">
          <button onClick={() => setExpanded(expanded === cat.category ? null : cat.category)}
            className="flex w-full items-center justify-between px-4 py-2.5 text-left">
            <span className="font-medium">{cat.label}</span>
            <span className="text-xs text-gray-400">{cat.events.length} events {expanded === cat.category ? "▲" : "▼"}</span>
          </button>
          {expanded === cat.category && (
            <div className="border-t px-4 py-2 dark:border-gray-700">
              {cat.events.map(e => (
                <div key={e.event} className="flex items-center justify-between py-1.5">
                  <div>
                    <code className="font-mono text-xs text-blue-600">{e.event}</code>
                    <p className="text-xs text-gray-400">{e.description}</p>
                  </div>
                  <button onClick={() => onSubscribe(e.event)} className="rounded bg-blue-600 px-2 py-0.5 text-xs text-white">
                    Subscribe
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
