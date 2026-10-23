"use client";

import { useState } from "react";

interface SanitizedInputProps { label: string; maxLength: number; placeholder?: string;
  onSubmit: (value: string) => void; multiline?: boolean; }

export function SanitizedInput({ label, maxLength, placeholder, onSubmit, multiline }: SanitizedInputProps) {
  const [value, setValue] = useState("");
  const remaining = maxLength - value.length;
  const overLimit = remaining < 0;

  return (
    <div className="space-y-1">
      <label className="text-sm font-medium">{label}</label>
      {multiline ? (
        <textarea value={value} onChange={e => setValue(e.target.value)}
          placeholder={placeholder} rows={4} maxLength={maxLength + 100}
          className="w-full rounded-lg border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
      ) : (
        <input value={value} onChange={e => setValue(e.target.value)}
          placeholder={placeholder} maxLength={maxLength + 100}
          className="w-full rounded-lg border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
      )}
      <div className="flex items-center justify-between">
        <span className={`text-xs ${overLimit ? "text-red-500" : remaining < 20 ? "text-yellow-500" : "text-gray-400"}`}>
          {remaining} characters remaining
        </span>
        <button onClick={() => onSubmit(value)} disabled={overLimit || !value.trim()}
          className="rounded bg-blue-600 px-3 py-1 text-xs text-white disabled:opacity-50">Submit</button>
      </div>
    </div>
  );
}
