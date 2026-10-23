"use client";

import { useState } from "react";

interface Step { order: number; title: string; code: string; }
interface SdkQuickstartPageProps { steps: Step[]; language: string;
  availableLanguages: string[]; onLanguageChange: (lang: string) => void; }

const langIcons: Record<string, string> = { typescript: "📘", python: "🐍", go: "🐹" };

export function SdkQuickstartPage({ steps, language, availableLanguages, onLanguageChange }: SdkQuickstartPageProps) {
  const [copied, setCopied] = useState<number | null>(null);
  const copy = (order: number, code: string) => {
    navigator.clipboard?.writeText(code); setCopied(order);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <h2 className="text-2xl font-bold">🚀 SDK Quickstart</h2>
      <div className="flex gap-1">
        {availableLanguages.map(l => (
          <button key={l} onClick={() => onLanguageChange(l)}
            className={`rounded px-3 py-1 text-xs capitalize ${language === l ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {langIcons[l] ?? "📄"} {l}
          </button>
        ))}
      </div>
      <div className="space-y-4">
        {steps.map(s => (
          <div key={s.order} className="rounded-xl border p-4 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-xs text-white">{s.order}</span>
                <h3 className="text-sm font-semibold">{s.title}</h3>
              </div>
              <button onClick={() => copy(s.order, s.code)} className="text-xs text-gray-400">
                {copied === s.order ? "✓" : "📋"}
              </button>
            </div>
            <pre className="rounded-lg bg-gray-950 p-3 text-xs font-mono text-green-400 overflow-x-auto">{s.code}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}
