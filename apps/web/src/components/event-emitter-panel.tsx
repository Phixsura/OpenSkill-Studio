"use client";

import { useState } from "react";

interface EventListener {
  listenerId: string;
  eventPattern: string;
  handlerName: string;
  once: boolean;
  callCount: number;
}

interface EmittedEvent {
  eventName: string;
  listenersNotified: number;
}

export function EventEmitterPanel({
  listeners,
  history,
  onEmit,
  onRemove,
}: {
  listeners: EventListener[];
  history: EmittedEvent[];
  onEmit?: (eventName: string) => void;
  onRemove?: (listenerId: string) => void;
}) {
  const [tab, setTab] = useState<"listeners" | "history">("listeners");
  const [eventName, setEventName] = useState("");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📡 Event Emitter</h2>

      <div className="flex gap-2">
        <input type="text" value={eventName} onChange={(e) => setEventName(e.target.value)}
          placeholder="event:name"
          className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm font-mono" />
        <button onClick={() => { onEmit?.(eventName); setEventName(""); }}
          disabled={!eventName.trim()}
          className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg disabled:opacity-50">Emit</button>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("listeners")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "listeners" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Listeners ({listeners.length})
        </button>
        <button onClick={() => setTab("history")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "history" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          History ({history.length})
        </button>
      </div>

      {tab === "listeners" && (
        <div className="space-y-1">
          {listeners.map((l) => (
            <div key={l.listenerId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm">
                <code className="text-blue-600">{l.eventPattern}</code>
                <span className="text-gray-400">→</span>
                <code className="text-gray-500">{l.handlerName}</code>
                {l.once && <span className="text-xs text-yellow-600">once</span>}
                <span className="text-xs text-gray-400">×{l.callCount}</span>
              </div>
              <button onClick={() => onRemove?.(l.listenerId)} className="text-xs text-red-500">✕</button>
            </div>
          ))}
        </div>
      )}

      {tab === "history" && (
        <div className="space-y-0.5">
          {history.map((evt, i) => (
            <div key={i} className="flex items-center justify-between text-xs rounded-lg border dark:border-gray-700 p-2">
              <code>{evt.eventName}</code>
              <span className="text-gray-400">{evt.listenersNotified} notified</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
