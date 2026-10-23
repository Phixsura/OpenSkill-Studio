"use client";

import { useState } from "react";

interface FormField { name: string; label: string; type: string; required: boolean;
  placeholder: string; options: string[]; default?: unknown; }
interface DynamicFormRendererProps { title: string; fields: FormField[];
  onSubmit: (data: Record<string, unknown>) => void; }

export function DynamicFormRenderer({ title, fields, onSubmit }: DynamicFormRendererProps) {
  const [values, setValues] = useState<Record<string, unknown>>(
    Object.fromEntries(fields.map(f => [f.name, f.default ?? (f.type === "checkbox" ? false : "")]))
  );
  const set = (name: string, value: unknown) => setValues({ ...values, [name]: value });

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div className="space-y-3">
        {fields.map(f => (
          <div key={f.name}>
            <label className="text-sm font-medium">
              {f.label} {f.required && <span className="text-red-500">*</span>}
            </label>
            {f.type === "select" ? (
              <select value={String(values[f.name] ?? "")} onChange={e => set(f.name, e.target.value)}
                className="mt-0.5 w-full rounded border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700">
                <option value="">Select...</option>
                {f.options.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            ) : f.type === "textarea" ? (
              <textarea value={String(values[f.name] ?? "")} onChange={e => set(f.name, e.target.value)}
                placeholder={f.placeholder} rows={3}
                className="mt-0.5 w-full rounded border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
            ) : f.type === "checkbox" ? (
              <label className="mt-0.5 flex items-center gap-2">
                <input type="checkbox" checked={Boolean(values[f.name])}
                  onChange={e => set(f.name, e.target.checked)} className="accent-blue-600" />
                <span className="text-sm">{f.placeholder || f.label}</span>
              </label>
            ) : (
              <input type={f.type} value={String(values[f.name] ?? "")}
                onChange={e => set(f.name, e.target.value)} placeholder={f.placeholder}
                className="mt-0.5 w-full rounded border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
            )}
          </div>
        ))}
      </div>
      <button onClick={() => onSubmit(values)}
        className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white">Submit</button>
    </div>
  );
}
