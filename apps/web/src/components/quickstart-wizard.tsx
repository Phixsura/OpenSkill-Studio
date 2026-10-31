"use client";

import { useState } from "react";

interface QuickstartStep { id: string; title: string; code: string; icon: string; order: number; completed: boolean; }
interface QuickstartWizardProps { steps: QuickstartStep[]; progressPct: number; onComplete: (id: string) => void; }

export function QuickstartWizard({ steps, progressPct, onComplete }: QuickstartWizardProps) {
  const [copied, setCopied] = useState<string | null>(null);
  const copy = (id: string, code: string) => {
    navigator.clipboard?.writeText(code); setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-bold">🚀 Quickstart</h2>
        <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className="h-full rounded-full bg-green-500 transition-all" style={{ width: `${progressPct}%` }} />
        </div>
        <p className="mt-1 text-xs text-gray-400">{progressPct}% complete</p>
      </div>
      <div className="space-y-3">
        {steps.map(s => (
          <div key={s.id} className={`rounded-lg border p-4 ${s.completed ? "opacity-60" : ""} dark:border-gray-700`}>
            <div className="flex items-center gap-3">
              <span className={`flex h-7 w-7 items-center justify-center rounded-full text-sm ${s.completed ? "bg-green-500 text-white" : "bg-gray-200 dark:bg-gray-700"}`}>
                {s.completed ? "✓" : s.order}
              </span>
              <div className="flex-1">
                <p className={`text-sm font-medium ${s.completed ? "line-through text-gray-400" : ""}`}>{s.title}</p>
                <div className="mt-1 flex items-center gap-2">
                  <code className="rounded bg-gray-950 px-2 py-0.5 text-xs text-green-400">{s.code}</code>
                  <button onClick={() => copy(s.id, s.code)} className="text-xs text-gray-400">{copied === s.id ? "✓" : "📋"}</button>
                </div>
              </div>
              {!s.completed && (
                <button onClick={() => onComplete(s.id)} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Done</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
