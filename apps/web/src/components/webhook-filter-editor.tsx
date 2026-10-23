"use client";

interface WebhookFilterEditorProps { eventTypes: string[]; selectedTypes: string[];
  dropRate: number; onToggle: (type: string) => void; }

export function WebhookFilterEditor({ eventTypes, selectedTypes, dropRate, onToggle }: WebhookFilterEditorProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🔍 Webhook Filters</h3>
        <span className="text-xs text-gray-400">{dropRate}% filtered out</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {eventTypes.map(t => {
          const active = selectedTypes.includes(t);
          return (
            <button key={t} onClick={() => onToggle(t)}
              className={`text-xs px-3 py-1.5 rounded-full transition ${
                active ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
              }`}>{t}</button>
          );
        })}
      </div>
    </div>
  );
}
