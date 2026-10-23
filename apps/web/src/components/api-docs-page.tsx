"use client";

import { useState } from "react";

interface EndpointGroup { name: string; endpoints: { method: string; path: string; summary: string }[]; }
interface ApiDocsPageProps { title: string; version: string; groups: EndpointGroup[]; totalEndpoints: number; }

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-100 text-green-700", POST: "bg-blue-100 text-blue-700",
  PUT: "bg-yellow-100 text-yellow-700", DELETE: "bg-red-100 text-red-700",
};

export function ApiDocsPage({ title, version, groups, totalEndpoints }: ApiDocsPageProps) {
  const [activeGroup, setActiveGroup] = useState(groups[0]?.name || "");
  const currentGroup = groups.find(g => g.name === activeGroup);

  return (
    <div className="flex gap-6">
      <nav className="w-48 space-y-0.5">
        <h2 className="px-3 py-1 text-xs font-semibold text-gray-400">{title} {version}</h2>
        <p className="px-3 text-xs text-gray-400">{totalEndpoints} endpoints</p>
        {groups.map(g => (
          <button key={g.name} onClick={() => setActiveGroup(g.name)}
            className={`flex w-full items-center justify-between rounded px-3 py-1.5 text-left text-sm ${
              activeGroup === g.name ? "bg-blue-50 font-semibold text-blue-700 dark:bg-blue-900/20" : "text-gray-600 dark:text-gray-400"}`}>
            <span className="capitalize">{g.name}</span>
            <span className="text-xs text-gray-400">{g.endpoints.length}</span>
          </button>
        ))}
      </nav>
      <div className="flex-1 space-y-2">
        {currentGroup?.endpoints.map((ep, i) => (
          <div key={i} className="flex items-center gap-3 rounded-lg border border-gray-200 p-3 dark:border-gray-700">
            <span className={`rounded px-2 py-0.5 text-xs font-mono font-bold ${METHOD_COLORS[ep.method] || "bg-gray-100"}`}>{ep.method}</span>
            <code className="text-sm">{ep.path}</code>
            <span className="ml-auto text-xs text-gray-400">{ep.summary}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
