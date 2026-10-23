"use client";

import { useState } from "react";

interface WebhookSetupWizardProps { availableEvents: string[]; categories: Record<string, string[]>;
  onComplete: (url: string, events: string[]) => void; }

export function WebhookSetupWizard({ availableEvents, categories, onComplete }: WebhookSetupWizardProps) {
  const [url, setUrl] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [step, setStep] = useState<"url" | "events" | "confirm">("url");

  const toggle = (e: string) => {
    const next = new Set(selected);
    next.has(e) ? next.delete(e) : next.add(e);
    setSelected(next);
  };

  return (
    <div className="mx-auto max-w-md space-y-4">
      <h2 className="text-lg font-bold">🔗 Setup Webhook</h2>
      <div className="flex gap-2 text-xs">
        {["url", "events", "confirm"].map((s, i) => (
          <span key={s} className={`rounded-full px-3 py-1 ${step === s ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {i + 1}. {s.charAt(0).toUpperCase() + s.slice(1)}
          </span>
        ))}
      </div>
      {step === "url" && (
        <div className="space-y-3">
          <input value={url} onChange={e => setUrl(e.target.value)} placeholder="https://your-app.com/webhook"
            className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
          <button onClick={() => url.startsWith("https://") && setStep("events")} disabled={!url.startsWith("https://")}
            className="w-full rounded bg-blue-600 py-2 text-sm text-white disabled:opacity-30">Next</button>
        </div>
      )}
      {step === "events" && (
        <div className="space-y-3">
          {Object.entries(categories).map(([cat, events]) => (
            <div key={cat}>
              <p className="text-xs font-semibold text-gray-400 mb-1">{cat}</p>
              {events.map(e => (
                <label key={e} className="flex items-center gap-2 py-1">
                  <input type="checkbox" checked={selected.has(e)} onChange={() => toggle(e)} className="accent-blue-600" />
                  <code className="text-xs font-mono">{e}</code>
                </label>
              ))}
            </div>
          ))}
          <button onClick={() => selected.size > 0 && setStep("confirm")} disabled={selected.size === 0}
            className="w-full rounded bg-blue-600 py-2 text-sm text-white disabled:opacity-30">Next ({selected.size} events)</button>
        </div>
      )}
      {step === "confirm" && (
        <div className="space-y-3">
          <div className="rounded bg-gray-50 p-3 dark:bg-gray-800 text-xs">
            <p><strong>URL:</strong> {url}</p>
            <p className="mt-1"><strong>Events:</strong> {Array.from(selected).join(", ")}</p>
          </div>
          <button onClick={() => onComplete(url, Array.from(selected))}
            className="w-full rounded bg-green-600 py-2 text-sm text-white">Create Webhook</button>
        </div>
      )}
    </div>
  );
}
