"use client";

import { useState } from "react";

interface ConsentCategory { id: string; label: string; required: boolean; description: string; }
interface ConsentPreferencesFormProps { categories: ConsentCategory[];
  onSave: (choices: Record<string, boolean>) => void; }

export function ConsentPreferencesForm({ categories, onSave }: ConsentPreferencesFormProps) {
  const [choices, setChoices] = useState<Record<string, boolean>>(
    Object.fromEntries(categories.map(c => [c.id, c.required]))
  );

  const toggle = (id: string) => {
    if (categories.find(c => c.id === id)?.required) return;
    setChoices({ ...choices, [id]: !choices[id] });
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Privacy Preferences</h2>
      <div className="space-y-2">
        {categories.map(c => (
          <div key={c.id} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{c.label}</span>
                {c.required && <span className="text-xs text-gray-400">(Required)</span>}
              </div>
              <p className="text-xs text-gray-400">{c.description}</p>
            </div>
            <button onClick={() => toggle(c.id)} disabled={c.required}
              className={`relative h-6 w-11 rounded-full transition-colors ${choices[c.id] ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"} ${c.required ? "opacity-60" : ""}`}>
              <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${choices[c.id] ? "left-[1.375rem]" : "left-0.5"}`} />
            </button>
          </div>
        ))}
      </div>
      <button onClick={() => onSave(choices)}
        className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white">
        Save Preferences
      </button>
    </div>
  );
}
