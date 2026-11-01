"use client";

import { useState } from "react";

interface StateHistory {
  fromState: string;
  toState: string;
  event: string;
  timestamp: string;
}

interface StateMachineInfo {
  machineId: string;
  name: string;
  currentState: string;
  states: string[];
  availableEvents: string[];
  history: StateHistory[];
}

export function StateMachinePanel({
  machine,
  onSendEvent,
  onReset,
}: {
  machine: StateMachineInfo;
  onSendEvent?: (event: string) => void;
  onReset?: () => void;
}) {
  const [tab, setTab] = useState<"diagram" | "history">("diagram");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold">🔀 {machine.name}</h2>
          <span className="text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-700 px-2 py-0.5 rounded-full font-bold">
            {machine.currentState}
          </span>
        </div>
        <button onClick={onReset} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Reset</button>
      </div>

      {machine.availableEvents.length > 0 && (
        <div>
          <span className="text-xs text-gray-500">Available transitions:</span>
          <div className="flex gap-1 mt-1">
            {machine.availableEvents.map((event) => (
              <button key={event} onClick={() => onSendEvent?.(event)}
                className="text-xs bg-green-600 text-white px-3 py-1.5 rounded-lg hover:bg-green-700">
                {event}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-1">
        <button onClick={() => setTab("diagram")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "diagram" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          States
        </button>
        <button onClick={() => setTab("history")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "history" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          History ({machine.history.length})
        </button>
      </div>

      {tab === "diagram" && (
        <div className="flex flex-wrap gap-2">
          {machine.states.map((state) => (
            <div key={state}
              className={`rounded-lg border-2 px-4 py-2 text-sm font-medium ${
                state === machine.currentState
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700"
                  : "border-gray-200 dark:border-gray-700 text-gray-500"
              }`}>
              {state === machine.currentState && "● "}{state}
            </div>
          ))}
        </div>
      )}

      {tab === "history" && (
        <div className="space-y-1">
          {machine.history.map((h, i) => (
            <div key={i} className="flex items-center gap-2 text-xs rounded-lg border dark:border-gray-700 p-2">
              <span className="font-mono">{h.fromState}</span>
              <span className="text-blue-600">→ {h.event}</span>
              <span className="font-mono font-bold">{h.toState}</span>
              <span className="text-gray-400 ml-auto">{h.timestamp}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
