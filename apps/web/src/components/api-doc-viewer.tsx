"use client";

import { useState } from "react";

interface ApiEndpoint {
  method: string;
  path: string;
  summary: string;
  description?: string;
  tags: string[];
  authRequired: boolean;
  deprecated: boolean;
  params: { name: string; location: string; type: string; required: boolean }[];
}

const methodColors: Record<string, string> = {
  get: "bg-green-500", post: "bg-blue-500", put: "bg-yellow-500",
  delete: "bg-red-500", patch: "bg-purple-500",
};

export function ApiDocViewer({
  endpoints,
  title,
  version,
  onTryIt,
}: {
  endpoints: ApiEndpoint[];
  title: string;
  version: string;
  onTryIt?: (method: string, path: string) => void;
}) {
  const [expanded, setExpanded] = useState<string | null>(null);
  const [tagFilter, setTagFilter] = useState<string>("all");

  const allTags = [...new Set(endpoints.flatMap((e) => e.tags))].sort();
  const filtered = tagFilter === "all" ? endpoints : endpoints.filter((e) => e.tags.includes(tagFilter));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📖 {title}</h2>
        <span className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">{version}</span>
      </div>

      {allTags.length > 0 && (
        <div className="flex gap-1 flex-wrap">
          <button onClick={() => setTagFilter("all")}
            className={`text-xs px-2.5 py-1 rounded-full ${tagFilter === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            All ({endpoints.length})
          </button>
          {allTags.map((tag) => (
            <button key={tag} onClick={() => setTagFilter(tag)}
              className={`text-xs px-2.5 py-1 rounded-full ${tagFilter === tag ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
              {tag}
            </button>
          ))}
        </div>
      )}

      <div className="space-y-1">
        {filtered.map((ep) => {
          const key = `${ep.method}-${ep.path}`;
          const isExpanded = expanded === key;
          return (
            <div key={key} className={`rounded-lg border dark:border-gray-700 overflow-hidden ${ep.deprecated ? "opacity-60" : ""}`}>
              <div className="flex items-center gap-2 p-3 cursor-pointer"
                onClick={() => setExpanded(isExpanded ? null : key)}>
                <span className={`text-xs text-white px-2 py-0.5 rounded font-bold uppercase ${methodColors[ep.method] || "bg-gray-500"}`}>
                  {ep.method}
                </span>
                <code className="text-sm flex-1">{ep.path}</code>
                <span className="text-xs text-gray-500">{ep.summary}</span>
                {ep.deprecated && <span className="text-xs text-red-500">deprecated</span>}
                {ep.authRequired && <span className="text-xs text-gray-400">🔒</span>}
              </div>

              {isExpanded && (
                <div className="border-t dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 space-y-2">
                  {ep.description && <p className="text-sm text-gray-600 dark:text-gray-400">{ep.description}</p>}
                  {ep.params.length > 0 && (
                    <div>
                      <span className="text-xs font-semibold text-gray-500">Parameters</span>
                      {ep.params.map((p) => (
                        <div key={p.name} className="text-xs mt-0.5 flex gap-2">
                          <code className="font-bold">{p.name}</code>
                          <span className="text-gray-400">{p.location} · {p.type}</span>
                          {p.required && <span className="text-red-500">required</span>}
                        </div>
                      ))}
                    </div>
                  )}
                  <button onClick={() => onTryIt?.(ep.method, ep.path)}
                    className="text-xs bg-blue-600 text-white px-3 py-1 rounded">Try It</button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
