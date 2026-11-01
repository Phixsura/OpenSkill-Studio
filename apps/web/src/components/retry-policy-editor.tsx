"use client";

import { useState } from "react";

interface RetryPolicyEditorProps {
  initialMaxRetries: number; initialDelayMs: number; maxDelayMs: number;
  onSave: (policy: { maxRetries: number; initialDelayMs: number; maxDelayMs: number }) => void;
}

export function RetryPolicyEditor({ initialMaxRetries, initialDelayMs, maxDelayMs, onSave }: RetryPolicyEditorProps) {
  const [retries, setRetries] = useState(initialMaxRetries);
  const [delay, setDelay] = useState(initialDelayMs);
  const [maxDelay, setMaxDelay] = useState(maxDelayMs);

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Retry Policy</h3>
      <div className="mt-3 space-y-3">
        <div>
          <label className="block text-xs font-medium text-gray-500">Max Retries</label>
          <input type="number" min={0} max={20} value={retries} onChange={e => setRetries(Number(e.target.value))}
            className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">Initial Delay (ms)</label>
          <input type="number" min={100} value={delay} onChange={e => setDelay(Number(e.target.value))}
            className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">Max Delay (ms)</label>
          <input type="number" min={1000} value={maxDelay} onChange={e => setMaxDelay(Number(e.target.value))}
            className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
      </div>
      <button onClick={() => onSave({ maxRetries: retries, initialDelayMs: delay, maxDelayMs: maxDelay })}
        className="mt-3 rounded bg-blue-600 px-4 py-2 text-sm text-white">Save Policy</button>
    </div>
  );
}
