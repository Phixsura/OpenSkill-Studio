"use client";

import { useState } from "react";

interface ApiEndpoint {
  path: string;
  method: "GET" | "POST" | "PUT" | "DELETE";
  description: string;
  params: { name: string; type: string; required: boolean }[];
  responseExample: string;
}

interface ApiGroup {
  name: string;
  endpoints: ApiEndpoint[];
}

export function ExtensionApiExplorer({
  groups,
  extensionName,
}: {
  groups: ApiGroup[];
  extensionName: string;
}) {
  const [activeGroup, setActiveGroup] = useState(groups[0]?.name || "");
  const [expandedPath, setExpandedPath] = useState<string | null>(null);

  const methodColors: Record<string, string> = {
    GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500", DELETE: "bg-red-500",
  };

  const currentGroup = groups.find((g) => g.name === activeGroup);

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 border-b dark:border-gray-700">
        <h2 className="font-bold">📚 {extensionName} API Explorer</h2>
      </div>

      <div className="flex divide-x dark:divide-gray-700">
        {/* Group tabs */}
        <div className="w-40 bg-gray-50/50 dark:bg-gray-800/50 p-2">
          {groups.map((g) => (
            <button key={g.name} onClick={() => setActiveGroup(g.name)}
              className={`w-full text-left px-3 py-2 rounded text-sm ${
                activeGroup === g.name ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300" : "text-gray-500"
              }`}>
              {g.name} <span className="text-xs text-gray-400">({g.endpoints.length})</span>
            </button>
          ))}
        </div>

        {/* Endpoints */}
        <div className="flex-1 max-h-96 overflow-y-auto">
          {currentGroup?.endpoints.map((ep) => {
            const expanded = expandedPath === `${ep.method}:${ep.path}`;
            return (
              <div key={`${ep.method}:${ep.path}`} className="border-b dark:border-gray-800">
                <button onClick={() => setExpandedPath(expanded ? null : `${ep.method}:${ep.path}`)}
                  className="w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-gray-50 dark:hover:bg-gray-800">
                  <span className={`text-white text-xs px-1.5 py-0.5 rounded font-mono ${methodColors[ep.method]}`}>
                    {ep.method}
                  </span>
                  <span className="font-mono text-sm">{ep.path}</span>
                  <span className="text-xs text-gray-400 flex-1 truncate">{ep.description}</span>
                  <span className="text-gray-400 text-xs">{expanded ? "▼" : "▶"}</span>
                </button>
                {expanded && (
                  <div className="px-4 pb-3 space-y-2 bg-gray-50/50 dark:bg-gray-900/50">
                    {ep.params.length > 0 && (
                      <div>
                        <div className="text-xs font-medium text-gray-500 mb-1">Parameters</div>
                        {ep.params.map((p) => (
                          <div key={p.name} className="text-xs flex gap-2 ml-2">
                            <code className="text-blue-500">{p.name}</code>
                            <span className="text-gray-400">{p.type}</span>
                            {p.required && <span className="text-red-400">required</span>}
                          </div>
                        ))}
                      </div>
                    )}
                    <div>
                      <div className="text-xs font-medium text-gray-500 mb-1">Response</div>
                      <pre className="bg-gray-900 text-green-400 text-xs p-2 rounded font-mono overflow-auto max-h-24">
                        {ep.responseExample}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
