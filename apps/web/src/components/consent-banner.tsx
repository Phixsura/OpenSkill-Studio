"use client";

interface ConsentItem { type: string; description: string; required: boolean; granted: boolean; editable: boolean; }
interface ConsentBannerProps { items: ConsentItem[]; onAcceptAll: () => void;
  onSave: (consents: Record<string, boolean>) => void; }

export function ConsentBanner({ items, onAcceptAll, onSave }: ConsentBannerProps) {
  return (
    <div className="fixed bottom-0 inset-x-0 z-50 border-t bg-white p-4 shadow-lg dark:bg-gray-900 dark:border-gray-700">
      <div className="mx-auto max-w-2xl space-y-3">
        <p className="text-sm font-semibold">🍪 Cookie & Privacy Preferences</p>
        <div className="space-y-2">
          {items.map(i => (
            <label key={i.type} className="flex items-center justify-between">
              <div>
                <span className="text-sm capitalize">{i.type}</span>
                <p className="text-xs text-gray-400">{i.description}</p>
              </div>
              <input type="checkbox" defaultChecked={i.granted} disabled={i.required}
                className="accent-blue-600" />
            </label>
          ))}
        </div>
        <div className="flex justify-end gap-2">
          <button onClick={() => onSave(Object.fromEntries(items.map(i => [i.type, i.granted])))}
            className="rounded border px-4 py-1.5 text-sm dark:border-gray-700">Save Preferences</button>
          <button onClick={onAcceptAll}
            className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white">Accept All</button>
        </div>
      </div>
    </div>
  );
}
