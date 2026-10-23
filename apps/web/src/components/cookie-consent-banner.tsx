"use client";

interface CookieCategory { id: string; label: string; required: boolean; description: string; consented: boolean; }
interface CookieConsentBannerProps { categories: CookieCategory[]; domain: string;
  onAcceptAll: () => void; onReject: () => void; onCustomize: (consents: Record<string, boolean>) => void; }

export function CookieConsentBanner({ categories, domain, onAcceptAll, onReject, onCustomize }: CookieConsentBannerProps) {
  return (
    <div className="fixed bottom-0 inset-x-0 z-50 border-t bg-white p-4 shadow-2xl dark:bg-gray-900 dark:border-gray-700">
      <div className="mx-auto max-w-2xl">
        <p className="text-sm">🍪 We use cookies on <strong>{domain}</strong> to improve your experience.</p>
        <div className="mt-3 space-y-2">
          {categories.map(c => (
            <div key={c.id} className="flex items-center justify-between text-sm">
              <div>
                <span className="font-medium">{c.label}</span>
                {c.required && <span className="ml-1 text-xs text-gray-400">(required)</span>}
              </div>
              <input type="checkbox" defaultChecked={c.consented} disabled={c.required} className="accent-blue-600" />
            </div>
          ))}
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <button onClick={onReject} className="rounded border px-3 py-1.5 text-sm dark:border-gray-700">Reject</button>
          <button onClick={onAcceptAll} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Accept All</button>
        </div>
      </div>
    </div>
  );
}
