"use client";

import { useState } from "react";

interface GalleryExtension {
  id: string;
  name: string;
  icon: string;
  author: string;
  description: string;
  rating: number;
  downloads: number;
  category: string;
  featured: boolean;
}

export function ExtensionGallery({
  extensions,
  categories,
  onSelect,
}: {
  extensions: GalleryExtension[];
  categories: string[];
  onSelect?: (id: string) => void;
}) {
  const [activeCategory, setActiveCategory] = useState("all");
  const [sortBy, setSortBy] = useState<"popular" | "rating" | "newest">("popular");

  const filtered = activeCategory === "all"
    ? extensions
    : extensions.filter((e) => e.category === activeCategory);

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === "rating") return b.rating - a.rating;
    return b.downloads - a.downloads;
  });

  const featured = extensions.filter((e) => e.featured).slice(0, 3);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">🏪 Extension Gallery</h2>

      {/* Featured */}
      {featured.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {featured.map((ext) => (
            <button key={ext.id} onClick={() => onSelect?.(ext.id)}
              className="text-left rounded-xl border-2 border-blue-200 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-900/10 p-4 hover:shadow-md transition">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">{ext.icon}</span>
                <div>
                  <div className="font-bold text-sm">{ext.name}</div>
                  <div className="text-xs text-gray-500">by {ext.author}</div>
                </div>
              </div>
              <p className="text-xs text-gray-500 line-clamp-2">{ext.description}</p>
              <div className="flex gap-3 mt-2 text-xs text-gray-400">
                <span>★ {ext.rating.toFixed(1)}</span>
                <span>⬇ {ext.downloads.toLocaleString()}</span>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex gap-1 overflow-x-auto">
          <button onClick={() => setActiveCategory("all")}
            className={`text-xs px-3 py-1.5 rounded-full whitespace-nowrap ${activeCategory === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            All
          </button>
          {categories.map((cat) => (
            <button key={cat} onClick={() => setActiveCategory(cat)}
              className={`text-xs px-3 py-1.5 rounded-full whitespace-nowrap ${activeCategory === cat ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
              {cat}
            </button>
          ))}
        </div>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
          className="text-xs rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1.5">
          <option value="popular">Most Popular</option>
          <option value="rating">Highest Rated</option>
        </select>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {sorted.map((ext) => (
          <button key={ext.id} onClick={() => onSelect?.(ext.id)}
            className="text-left rounded-xl border dark:border-gray-700 p-3 hover:shadow-sm transition">
            <div className="text-2xl mb-2">{ext.icon}</div>
            <div className="font-medium text-sm truncate">{ext.name}</div>
            <div className="text-xs text-gray-500 truncate">{ext.author}</div>
            <div className="flex gap-2 mt-2 text-xs text-gray-400">
              <span>★ {ext.rating.toFixed(1)}</span>
              <span>⬇ {ext.downloads.toLocaleString()}</span>
            </div>
          </button>
        ))}
      </div>

      <div className="text-center text-sm text-gray-400">{sorted.length} extensions</div>
    </div>
  );
}
