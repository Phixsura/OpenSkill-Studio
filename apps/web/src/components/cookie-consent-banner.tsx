"use client";

interface CookieCategory { id: string; label: string; description: string; required: boolean; defaultVal: boolean; }
interface CookieConsentBannerProps { categories: CookieCategory[];
  onAcceptAll: () => void; onRejectAll: () => void;
  onSave: (choices: Record<string, boolean>) => void; }

export function CookieConsentBanner({ categories, onAcceptAll, onRejectAll, onSave }: CookieConsentBannerProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t dark:border-gray-700 p-4 shadow-lg z-50">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold mb-1">🍪 Cookie Preferences</h3>
            <p className="text-xs text-gray-500">We use cookies to improve your experience.</p>
          </div>
          <div className="flex gap-2 shrink-0">
            <button onClick={onRejectAll}
              className="text-xs px-3 py-1.5 border rounded hover:bg-gray-50 dark:hover:bg-gray-800">Reject All</button>
            <button onClick={onAcceptAll}
              className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">Accept All</button>
          </div>
        </div>
        <div className="flex gap-4 mt-3">
          {categories.map(c => (
            <label key={c.id} className="flex items-center gap-1.5 text-xs">
              <input type="checkbox" defaultChecked={c.defaultVal || c.required} disabled={c.required}
                className="rounded" />
              <span className={c.required ? "text-gray-400" : ""}>{c.label}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
