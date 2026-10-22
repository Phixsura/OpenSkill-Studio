"use client";

import { useState } from "react";

interface EventCategory { description: string; events: Record<string, string>; }

interface EventCatalogProps { catalog: Record<string, EventCategory>; }

export function EventCatalog({ catalog }: EventCatalogProps) {
  const [search, setSearch] = useState("");
  const q = search.toLowerCase();
  return (
    <div>
      <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search events..."
        className="mb-4 w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800" />
      {Object.entries(catalog).map(([cat, info]) => {
        const events = Object.entries(info.events).filter(([e, d]) => !q || e.includes(q) || d.toLowerCase().includes(q));
        if (events.length === 0) return null;
        return (
          <div key={cat} className="mb-4">
            <h3 className="mb-1 text-sm font-semibold capitalize">{cat}</h3>
            <p className="mb-2 text-xs text-gray-500">{info.description}</p>
            {events.map(([event, desc]) => (
              <div key={event} className="ml-2 flex items-start gap-2 border-l-2 border-gray-200 py-1 pl-3 dark:border-gray-700">
                <code className="text-xs font-semibold text-blue-600">{event}</code>
                <span className="text-xs text-gray-500">{desc}</span>
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}
