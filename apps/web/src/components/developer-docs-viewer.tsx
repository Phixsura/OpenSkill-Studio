"use client";

import { useState } from "react";

interface DocPage {
  id: string;
  title: string;
  slug: string;
  category: string;
  content: string;
}

export function DeveloperDocsViewer({
  pages,
  initialPage,
}: {
  pages: DocPage[];
  initialPage?: string;
}) {
  const [activeId, setActiveId] = useState(initialPage || pages[0]?.id || "");
  const [search, setSearch] = useState("");

  const categories = [...new Set(pages.map((p) => p.category))];
  const activePage = pages.find((p) => p.id === activeId);

  const filteredPages = search
    ? pages.filter((p) => p.title.toLowerCase().includes(search.toLowerCase())
        || p.content.toLowerCase().includes(search.toLowerCase()))
    : pages;

  return (
    <div className="flex rounded-xl border dark:border-gray-700 overflow-hidden h-[500px]">
      {/* Sidebar */}
      <div className="w-64 border-r dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex flex-col">
        <div className="p-3 border-b dark:border-gray-700">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search docs..."
            className="w-full rounded-lg border dark:border-gray-600 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm"
          />
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {categories.map((cat) => {
            const catPages = filteredPages.filter((p) => p.category === cat);
            if (catPages.length === 0) return null;
            return (
              <div key={cat} className="mb-3">
                <div className="text-xs font-semibold text-gray-400 uppercase px-2 mb-1">{cat}</div>
                {catPages.map((page) => (
                  <button
                    key={page.id}
                    onClick={() => setActiveId(page.id)}
                    className={`w-full text-left px-2 py-1.5 rounded text-sm ${
                      activeId === page.id
                        ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium"
                        : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    }`}
                  >
                    {page.title}
                  </button>
                ))}
              </div>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 overflow-y-auto">
        {activePage ? (
          <div>
            <div className="text-xs text-gray-400 mb-1">{activePage.category}</div>
            <h1 className="text-2xl font-bold mb-4">{activePage.title}</h1>
            <div className="prose dark:prose-invert text-sm leading-relaxed whitespace-pre-wrap">
              {activePage.content}
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-400 mt-20">Select a page from the sidebar</div>
        )}
      </div>
    </div>
  );
}
