"use client";

import { useState } from "react";

interface ValidationResult { field: string; value: string; format: string; valid: boolean; error: string | null; }
interface DataValidationFormProps { results: ValidationResult[]; allValid: boolean;
  onValidate: (value: string, format: string) => void; }

const formats = ["email", "url", "uuid", "semver", "slug", "hex_color", "ipv4"];

export function DataValidationForm({ results, allValid, onValidate }: DataValidationFormProps) {
  const [value, setValue] = useState("");
  const [format, setFormat] = useState("email");

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Data Validator</h2>
      <div className="flex gap-2">
        <input value={value} onChange={e => setValue(e.target.value)} placeholder="Enter value..."
          className="flex-1 rounded border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <select value={format} onChange={e => setFormat(e.target.value)}
          className="rounded border px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700">
          {formats.map(f => <option key={f} value={f}>{f}</option>)}
        </select>
        <button onClick={() => onValidate(value, format)} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Check</button>
      </div>
      {results.length > 0 && (
        <div className="space-y-1">
          {results.map((r, i) => (
            <div key={i} className={`flex items-center gap-2 rounded border px-3 py-1.5 ${r.valid ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
              <span>{r.valid ? "✅" : "❌"}</span>
              <code className="text-xs">{r.value}</code>
              <span className="text-xs text-gray-400">({r.format})</span>
              {r.error && <span className="text-xs text-red-500">{r.error}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
