"use client";

import { useState } from "react";

interface CookieCategory { label: string; required: boolean; description: string; }
interface CookieConsentBannerProps { categories: Record<string, CookieCategory>; onAcceptAll: () => void; onSave: (consent: Record<string, boolean>) => void; }

export function CookieConsentBanner({ categories, onAcceptAll, onSave }: CookieConsentBannerProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [consent, setConsent] = useState<Record<string, boolean>>(
    Object.fromEntries(Object.entries(categories).map(([k, v]) => [k, v.required]))
  );

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 border-t bg-white p-4 shadow-lg dark:border-gray-700 dark:bg-gray-800">
      <div className="mx-auto max-w-4xl">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold">Cookie Preferences</h3>
            <p className="mt-1 text-sm text-gray-500">We use cookies to improve your experience.</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setShowDetails(!showDetails)} className="rounded border px-3 py-1.5 text-sm">
              {showDetails ? "Hide" : "Customize"}
            </button>
            <button onClick={onAcceptAll} className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white">Accept All</button>
          </div>
        </div>
        {showDetails && (
          <div className="mt-3 space-y-2">
            {Object.entries(categories).map(([key, cat]) => (
              <label key={key} className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={consent[key] || cat.required} disabled={cat.required}
                  onChange={e => setConsent({ ...consent, [key]: e.target.checked })} />
                <span className="font-medium">{cat.label}</span>
                <span className="text-xs text-gray-400">{cat.description}</span>
              </label>
            ))}
            <button onClick={() => onSave(consent)} className="rounded bg-gray-200 px-3 py-1 text-sm dark:bg-gray-700">
              Save Preferences
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
