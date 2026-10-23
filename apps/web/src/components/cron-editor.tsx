"use client";

import { useState } from "react";

interface CronField { field: string; value: string; range: string; }
interface CronEditorProps { fields: CronField[]; expression: string; description: string;
  onChange: (expression: string) => void; }

export function CronEditor({ fields, expression, description, onChange }: CronEditorProps) {
  const [values, setValues] = useState(expression.split(" "));

  const update = (idx: number, val: string) => {
    const next = [...values];
    next[idx] = val;
    setValues(next);
    onChange(next.join(" "));
  };

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Schedule (Cron)</h3>
      <div className="grid grid-cols-5 gap-2">
        {fields.map((f, i) => (
          <div key={f.field}>
            <label className="block text-xs text-gray-400 mb-1 capitalize">{f.field.replace("_", " ")}</label>
            <input value={values[i] ?? "*"} onChange={e => update(i, e.target.value)}
              className="w-full rounded border px-2 py-1.5 text-sm font-mono text-center dark:bg-gray-800 dark:border-gray-600" />
            <p className="mt-0.5 text-center text-xs text-gray-400">{f.range}</p>
          </div>
        ))}
      </div>
      <div className="rounded bg-gray-50 px-3 py-2 dark:bg-gray-900">
        <code className="text-sm font-mono">{values.join(" ")}</code>
        <p className="mt-1 text-xs text-gray-500">{description}</p>
      </div>
    </div>
  );
}
