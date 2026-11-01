"use client";
import { useState } from "react";

interface EventTemplate { eventType: string; fields: string[]; }
interface EventSimulatorPanelProps { templates: EventTemplate[];
  onSimulate: (eventType: string) => void; lastResult: { eventId: string; success: boolean; statusCode: number } | null; }

export function EventSimulatorPanel({ templates, onSimulate, lastResult }: EventSimulatorPanelProps) {
  const [selected, setSelected] = useState(templates[0]?.eventType || "");
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🎲 Event Simulator</h3>
      <div className="flex gap-2 mb-3">
        <select value={selected} onChange={e => setSelected(e.target.value)}
          className="flex-1 text-sm px-3 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600">
          {templates.map(t => <option key={t.eventType} value={t.eventType}>{t.eventType}</option>)}
        </select>
        <button onClick={() => onSimulate(selected)}
          className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Send</button>
      </div>
      {lastResult && (
        <div className={`p-3 rounded-lg text-sm ${lastResult.success ? "bg-green-50 text-green-700 dark:bg-green-900/20" : "bg-red-50 text-red-700 dark:bg-red-900/20"}`}>
          {lastResult.success ? "✅" : "❌"} {lastResult.statusCode} — {lastResult.eventId}
        </div>
      )}
    </div>
  );
}
