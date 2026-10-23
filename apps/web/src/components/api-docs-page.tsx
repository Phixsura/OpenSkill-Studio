"use client";

import { useState } from "react";

interface Endpoint { method: string; path: string; fullUrl: string; summary: string; }
interface DocSection { id: string; title: string; icon: string; endpoints: Endpoint[]; endpointCount: number; }
interface ApiDocsPageProps { sections: DocSection[]; totalEndpoints: number; baseUrl: string; }

const methodColors: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500",
  PATCH: "bg-orange-500", DELETE: "bg-red-500",
};

export function ApiDocsPage({ sections, totalEndpoints, baseUrl }: ApiDocsPageProps) {
  const [activeSection, setActiveSection] = useState(sections[0]?.id ?? "");
  const section = sections.find(s => s.id === activeSection);

  return (
    <div className="flex gap-6">
      <nav className="w-48 shrink-0 space-y-1">
        {sections.map(s => (
          <button key={s.id} onClick={() => setActiveSection(s.id)}
            className={`flex w-full items-center gap-2 rounded px-3 py-2 text-sm ${activeSection === s.id ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/20" : "text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
            <span>{s.icon}</span>{s.title}<span className="ml-auto text-xs text-gray-400">{s.endpointCount}</span>
          </button>
        ))}
      </nav>
      <div className="flex-1 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold">{section?.icon} {section?.title}</h2>
          <span className="text-xs text-gray-400">{totalEndpoints} total endpoints</span>
        </div>
        <div className="space-y-2">
          {section?.endpoints.map((ep, i) => (
            <div key={i} className="rounded-lg border p-3 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-xs text-white font-mono ${methodColors[ep.method] ?? "bg-gray-500"}`}>{ep.method}</span>
                <code className="text-sm font-mono">{ep.path}</code>
              </div>
              <p className="mt-1 text-xs text-gray-500">{ep.summary}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
