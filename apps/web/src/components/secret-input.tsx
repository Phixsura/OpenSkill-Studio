"use client";

import { useState } from "react";

interface SecretInputProps {
  label: string;
  name: string;
  required?: boolean;
  description?: string;
  onSave: (key: string, value: string) => void;
  saved?: boolean;
}

export function SecretInput({ label, name, required, description, onSave, saved }: SecretInputProps) {
  const [value, setValue] = useState("");
  const [revealed, setRevealed] = useState(false);

  return (
    <div className="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
      <div className="mb-1 flex items-center justify-between">
        <label className="text-sm font-medium">
          {label}
          {required && <span className="ml-1 text-red-500">*</span>}
        </label>
        {saved && (
          <span className="text-xs text-green-600 dark:text-green-400">✓ Saved</span>
        )}
      </div>
      {description && (
        <p className="mb-2 text-xs text-gray-500 dark:text-gray-400">{description}</p>
      )}
      <div className="flex gap-2">
        <input
          type={revealed ? "text" : "password"}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={saved ? "••••••••" : `Enter ${label}`}
          className="flex-1 rounded border border-gray-300 px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800"
          autoComplete="off"
        />
        <button
          type="button"
          onClick={() => setRevealed(!revealed)}
          className="rounded border px-2 py-1 text-xs text-gray-600 dark:text-gray-400"
        >
          {revealed ? "Hide" : "Show"}
        </button>
        <button
          type="button"
          onClick={() => { if (value) { onSave(name, value); setValue(""); } }}
          disabled={!value}
          className="rounded bg-blue-600 px-3 py-1 text-xs text-white disabled:opacity-50"
        >
          Save
        </button>
      </div>
    </div>
  );
}
