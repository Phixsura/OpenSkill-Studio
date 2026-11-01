"use client";

import { useState } from "react";

interface JournalEvent {
  sequence: number;
  eventType: string;
  actor: string;
  timestamp: string;
}

interface JournalStats {
  totalEvents: number;
  currentSequence: number;
  eventTypes: Record<string, number>;
}

export function EventJournalPanel({
  events,
  stats,
  onReplay,
}: {
  events: JournalEvent[];
  stats: JournalStats;
  onReplay?: (fromSeq: number) => void;
}) {
  const [tab, setTab] = useState<"events" | "stats">("events");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📜 Event Journal</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">seq #{stats.currentSequence}</span>
          <button onClick={() => onReplay?.(1)} className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Replay All</button>
        </div>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("events")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "events" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Events ({stats.totalEvents})
        </button>
        <button onClick={() => setTab("stats")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "stats" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Stats
        </button>
      </div>

      {tab === "events" && (
        <div className="space-y-0.5">
          {events.map((e) => (
            <div key={e.sequence} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="text-gray-400 font-mono w-8">#{e.sequence}</span>
                <span className="font-semibold">{e.eventType}</span>
                {e.actor && <span className="text-gray-400">by {e.actor}</span>}
              </div>
              <span className="text-gray-400">{e.timestamp}</span>
            </div>
          ))}
        </div>
      )}

      {tab === "stats" && (
        <div className="space-y-1">
          {Object.entries(stats.eventTypes).map(([type, count]) => (
            <div key={type} className="flex justify-between rounded-lg border dark:border-gray-700 p-2 text-sm">
              <span>{type}</span>
              <span className="font-bold">{count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
