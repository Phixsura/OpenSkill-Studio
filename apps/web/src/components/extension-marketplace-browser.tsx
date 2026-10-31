"use client";

import { useState } from "react";

interface Extension {
  id: string;
  name: string;
  author: string;
  version: string;
  description: string;
  downloads: number;
  rating: number;
  installed: boolean;
}

export function ExtensionMarketplaceBrowser({
  extensions,
  onInstall,
  onUninstall,
}: {
  extensions: Extension[];
  onInstall?: (id: string) => void;
  onUninstall?: (id: string) => void;
}) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");

  const filtered = extensions.filter(
    (ext) =>
      (search === "" ||
        ext.name.toLowerCase().includes(search.toLowerCase()) ||
        ext.description.toLowerCase().includes(search.toLowerCase())) &&
      (category === "all" || ext.author === category)
  );

  const authors = [...new Set(extensions.map((e) => e.author))];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <input
          type="text"
          placeholder="Search extensions..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-4 py-2 text-sm"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
        >
          <option value="all">All Authors</option>
          {authors.map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>
      </div>

      <div className="text-sm text-gray-500">{filtered.length} extensions found</div>

      <div className="grid gap-3">
        {filtered.map((ext) => (
          <div
            key={ext.id}
            className="rounded-xl border dark:border-gray-700 p-4 flex items-start justify-between"
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold">{ext.name}</h3>
                <span className="text-xs bg-gray-100 dark:bg-gray-800 rounded px-2 py-0.5">
                  v{ext.version}
                </span>
              </div>
              <p className="text-sm text-gray-500">{ext.description}</p>
              <div className="flex gap-3 text-xs text-gray-400">
                <span>by {ext.author}</span>
                <span>⬇ {ext.downloads.toLocaleString()}</span>
                <span>★ {ext.rating.toFixed(1)}</span>
              </div>
            </div>
            <button
              onClick={() => ext.installed ? onUninstall?.(ext.id) : onInstall?.(ext.id)}
              className={`shrink-0 rounded-lg px-4 py-2 text-sm font-medium ${
                ext.installed
                  ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
                  : "bg-blue-600 text-white hover:bg-blue-700"
              }`}
            >
              {ext.installed ? "Uninstall" : "Install"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
