"use client";

import { useState } from "react";

interface StarterTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  runtime: string;
  tags: string[];
  popularity: number;
  variableCount: number;
}

const categoryIcons: Record<string, string> = {
  integration: "🔗", automation: "🤖", analytics: "📊",
  ui_widget: "🎨", data_sync: "🔄", webhook: "🪝",
};

const runtimeBadges: Record<string, string> = {
  node20: "bg-green-100 text-green-700 dark:bg-green-900/30",
  "python3.12": "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  deno: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
};

export function StarterTemplateGallery({
  templates,
  onUse,
  onPreview,
}: {
  templates: StarterTemplate[];
  onUse?: (id: string) => void;
  onPreview?: (id: string) => void;
}) {
  const [search, setSearch] = useState("");
  const [catFilter, setCatFilter] = useState<string>("all");

  const categories = [...new Set(templates.map((t) => t.category))].sort();

  const filtered = templates.filter((t) => {
    if (catFilter !== "all" && t.category !== catFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      return t.name.toLowerCase().includes(q) || t.tags.some((tag) => tag.includes(q));
    }
    return true;
  });

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🚀 Starter Templates</h2>

      <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
        placeholder="Search templates..."
        className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm" />

      <div className="flex gap-1 flex-wrap">
        <button onClick={() => setCatFilter("all")}
          className={`text-xs px-2.5 py-1 rounded-full ${catFilter === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          All
        </button>
        {categories.map((cat) => (
          <button key={cat} onClick={() => setCatFilter(cat)}
            className={`text-xs px-2.5 py-1 rounded-full ${catFilter === cat ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {categoryIcons[cat] || "📦"} {cat}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {filtered.map((tpl) => (
          <div key={tpl.id} className="rounded-xl border dark:border-gray-700 p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">{categoryIcons[tpl.category] || "📦"}</span>
              <span className="font-semibold text-sm">{tpl.name}</span>
              <span className={`text-xs px-1.5 py-0.5 rounded ${runtimeBadges[tpl.runtime] || "bg-gray-100 dark:bg-gray-800"}`}>
                {tpl.runtime}
              </span>
            </div>
            <p className="text-xs text-gray-500 mb-2">{tpl.description}</p>
            <div className="flex items-center justify-between">
              <div className="flex gap-1">
                {tpl.tags.slice(0, 3).map((tag) => (
                  <span key={tag} className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{tag}</span>
                ))}
              </div>
              <div className="flex gap-1">
                <button onClick={() => onPreview?.(tpl.id)}
                  className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Preview</button>
                <button onClick={() => onUse?.(tpl.id)}
                  className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Use</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
