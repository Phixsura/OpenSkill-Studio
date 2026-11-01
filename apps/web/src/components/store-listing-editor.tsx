"use client";

interface StoreListingEditorProps { name: string; tagline: string;
  description: string; category: string; pricing: string;
  completenessPct: number; readyToPublish: boolean; features: string[];
  issues: string[]; onPublish: () => void; }

export function StoreListingEditor({ name, tagline, category, pricing, completenessPct, readyToPublish, features, issues, onPublish }: StoreListingEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏪 Store Listing</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{completenessPct}% complete</span>
          <button onClick={onPublish} disabled={!readyToPublish}
            className={`px-3 py-1 text-xs rounded ${readyToPublish ? "bg-green-500 text-white" : "bg-gray-300 text-gray-500"}`}>
            Publish
          </button>
        </div>
      </div>
      <div className="p-4 space-y-2">
        <div className="text-lg font-bold">{name}</div>
        <div className="text-sm text-gray-500">{tagline}</div>
        <div className="flex gap-2 text-xs">
          <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">{category}</span>
          <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded">{pricing}</span>
        </div>
        {features.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            {features.map(f => <span key={f} className="px-1.5 py-0.5 text-[10px] bg-gray-100 dark:bg-gray-800 rounded">{f}</span>)}
          </div>
        )}
      </div>
      {issues.length > 0 && (
        <div className="p-3 border-t dark:border-gray-700 bg-yellow-50 dark:bg-yellow-900/10">
          {issues.map((issue, i) => <div key={i} className="text-xs text-yellow-700">⚠ {issue}</div>)}
        </div>
      )}
    </div>
  );
}
