"use client";

import { useState } from "react";

interface DateRangePickerProps { presets: { id: string; label: string }[];
  activePreset: string; onPresetChange: (preset: string) => void; startDate: string; endDate: string; }

export function DateRangePicker({ presets, activePreset, onPresetChange, startDate, endDate }: DateRangePickerProps) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-1 rounded-lg border p-0.5 dark:border-gray-700">
        {presets.map(p => (
          <button key={p.id} onClick={() => onPresetChange(p.id)}
            className={`rounded-md px-2.5 py-1 text-xs ${activePreset === p.id ? "bg-blue-600 text-white" : "text-gray-400 hover:text-gray-600"}`}>
            {p.label}
          </button>
        ))}
      </div>
      <span className="text-xs text-gray-400">
        {new Date(startDate).toLocaleDateString()} — {new Date(endDate).toLocaleDateString()}
      </span>
    </div>
  );
}
