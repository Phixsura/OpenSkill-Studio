"use client";

import { useState } from "react";

interface Preset { id: string; label: string; days: number; }
interface DateRangePickerProps { presets: Preset[]; selected: string | null; onSelect: (preset: string) => void;
  onCustom: (start: string, end: string) => void; }

export function DateRangePicker({ presets, selected, onSelect, onCustom }: DateRangePickerProps) {
  const [custom, setCustom] = useState(false);
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {presets.map(p => (
          <button key={p.id} onClick={() => { setCustom(false); onSelect(p.id); }}
            className={`rounded-full px-3 py-1 text-xs font-medium transition ${selected === p.id && !custom ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"}`}>
            {p.label}
          </button>
        ))}
        <button onClick={() => setCustom(true)}
          className={`rounded-full px-3 py-1 text-xs font-medium ${custom ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
          Custom
        </button>
      </div>
      {custom && (
        <div className="flex items-center gap-2">
          <input type="date" value={start} onChange={e => setStart(e.target.value)}
            className="rounded border px-2 py-1 text-sm dark:bg-gray-800 dark:border-gray-600" />
          <span className="text-gray-400">—</span>
          <input type="date" value={end} onChange={e => setEnd(e.target.value)}
            className="rounded border px-2 py-1 text-sm dark:bg-gray-800 dark:border-gray-600" />
          <button onClick={() => start && end && onCustom(start, end)}
            className="rounded bg-blue-600 px-2 py-1 text-xs text-white">Apply</button>
        </div>
      )}
    </div>
  );
}
