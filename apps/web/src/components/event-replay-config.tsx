"use client";

import { useState } from "react";

interface EventReplayConfigProps { onReplay: (config: { eventType: string; since: string; dryRun: boolean }) => void; }

export function EventReplayConfig({ onReplay }: EventReplayConfigProps) {
  const [eventType, setEventType] = useState("");
  const [since, setSince] = useState("");
  const [dryRun, setDryRun] = useState(true);

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Event Replay</h3>
      <div className="mt-3 space-y-3">
        <div>
          <label className="block text-xs font-medium text-gray-500">Event Type</label>
          <input value={eventType} onChange={e => setEventType(e.target.value)} placeholder="e.g. app.installed"
            className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">Since</label>
          <input type="date" value={since} onChange={e => setSince(e.target.value)}
            className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={dryRun} onChange={e => setDryRun(e.target.checked)} />
          Dry run (preview only)
        </label>
      </div>
      <button onClick={() => onReplay({ eventType, since, dryRun })}
        className="mt-3 rounded bg-blue-600 px-4 py-2 text-sm text-white">
        {dryRun ? "Preview Replay" : "Start Replay"}
      </button>
    </div>
  );
}
