"use client";
import { useState } from "react";

interface ListingData { name: string; tagline: string; description: string; category: string; tags: string[]; }

const categories = ["developer-tools", "analytics", "integrations", "ui-components", "security", "automation"];

export function ListingBuilderForm({ initial, completeness, onSave, onPublish }: {
  initial?: Partial<ListingData>; completeness: number;
  onSave?: (data: ListingData) => void; onPublish?: () => void;
}) {
  const [data, setData] = useState<ListingData>({
    name: initial?.name || "", tagline: initial?.tagline || "",
    description: initial?.description || "", category: initial?.category || "",
    tags: initial?.tags || [],
  });
  const set = (k: keyof ListingData, v: string) => setData({ ...data, [k]: v });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-sm">Listing Builder</h3>
        <div className="flex items-center gap-2">
          <div className="w-24 h-2 bg-gray-100 dark:bg-gray-800 rounded-full">
            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${completeness}%` }} />
          </div>
          <span className="text-xs text-gray-500">{completeness}%</span>
        </div>
      </div>
      <input value={data.name} onChange={e => set("name", e.target.value)} placeholder="Extension name"
        className="w-full border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent" maxLength={50} />
      <input value={data.tagline} onChange={e => set("tagline", e.target.value)} placeholder="Short tagline"
        className="w-full border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent" />
      <textarea value={data.description} onChange={e => set("description", e.target.value)} placeholder="Full description (min 20 chars)"
        className="w-full border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent resize-none" rows={4} />
      <select value={data.category} onChange={e => set("category", e.target.value)}
        className="w-full border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent">
        <option value="">Select category</option>
        {categories.map(c => <option key={c} value={c}>{c}</option>)}
      </select>
      <div className="flex gap-2">
        <button onClick={() => onSave?.(data)} className="flex-1 bg-gray-200 dark:bg-gray-700 py-2 rounded-lg text-sm">Save Draft</button>
        <button onClick={onPublish} className="flex-1 bg-blue-500 text-white py-2 rounded-lg text-sm">Publish</button>
      </div>
    </div>
  );
}
