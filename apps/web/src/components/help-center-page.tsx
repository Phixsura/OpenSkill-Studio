"use client";

import { useState } from "react";

interface HelpSection { id: string; title: string; icon: string; article_count: number; description: string; }
interface HelpCenterPageProps { sections: HelpSection[]; totalArticles: number; onSearch: (query: string) => void; onSectionClick: (id: string) => void; }

export function HelpCenterPage({ sections, totalArticles, onSearch, onSectionClick }: HelpCenterPageProps) {
  const [query, setQuery] = useState("");

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold">How can we help?</h1>
        <p className="mt-1 text-sm text-gray-400">{totalArticles} articles across {sections.length} topics</p>
        <div className="mt-4">
          <input value={query} onChange={e => { setQuery(e.target.value); onSearch(e.target.value); }}
            placeholder="Search help articles..."
            className="w-full max-w-md rounded-lg border px-4 py-3 text-sm shadow-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        {sections.map(s => (
          <button key={s.id} onClick={() => onSectionClick(s.id)}
            className="rounded-lg border border-gray-200 p-4 text-left transition hover:shadow-md dark:border-gray-700">
            <span className="text-2xl">{s.icon}</span>
            <h3 className="mt-2 font-semibold">{s.title}</h3>
            <p className="mt-1 text-xs text-gray-500">{s.description}</p>
            <p className="mt-1 text-xs text-gray-400">{s.article_count} articles</p>
          </button>
        ))}
      </div>
    </div>
  );
}
