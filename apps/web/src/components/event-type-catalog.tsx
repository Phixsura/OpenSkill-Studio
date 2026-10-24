"use client";

import { useState } from "react";

interface EventType { id: string; description: string; category: string; fields: string[]; fieldCount: number; }
interface EventTypeCatalogProps { events: EventType[]; categories: string[]; }

export function EventTypeCatalog({ events, categories }: EventTypeCatalogProps) {
  const [filter, setFilter] = useState("all");
  const filtered = filter === "all" ? events : events.filter(e => e.category === filter);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Event Types</h3>
        <span className="text-xs text-gray-400">{filtered.length} events</span>
      </div>
      <div className="flex gap-1">
        <button onClick={() => setFilter("all")}
          className={`rounded px-2 py-0.5 text-xs ${filter === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
        {categories.map(c => (
          <button key={c} onClick={() => setFilter(c)}
            className={`rounded px-2 py-0.5 text-xs ${filter === c ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{c}</button>
        ))}
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {filtered.map(e => (
          <div key={e.id} className="px-4 py-2.5">
            <div className="flex items-center justify-between">
              <code className="text-sm font-mono font-medium text-blue-600">{e.id}</code>
              <span className="text-xs text-gray-400">{e.fieldCount} fields</span>
            </div>
            <p className="mt-0.5 text-xs text-gray-500">{e.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
