"use client";

import { useState } from "react";

interface ServiceInfo {
  name: string;
  implementation: string;
  lifetime: "singleton" | "transient" | "scoped";
  deps: string[];
}

const lifetimeConfig: Record<string, { color: string; label: string }> = {
  singleton: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", label: "Singleton" },
  transient: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", label: "Transient" },
  scoped: { color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30", label: "Scoped" },
};

export function DIContainerPanel({
  services,
  graph,
  onResolve,
  onClear,
}: {
  services: ServiceInfo[];
  graph: Record<string, string[]>;
  onResolve?: (name: string) => void;
  onClear?: () => void;
}) {
  const [tab, setTab] = useState<"services" | "graph">("services");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">💉 DI Container</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">{services.length} services</span>
          <button onClick={onClear} className="text-xs bg-red-600 text-white px-2 py-1 rounded">Clear</button>
        </div>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("services")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "services" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Services
        </button>
        <button onClick={() => setTab("graph")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "graph" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Dependency Graph
        </button>
      </div>

      {tab === "services" && (
        <div className="space-y-1">
          {services.map((svc) => {
            const lt = lifetimeConfig[svc.lifetime];
            return (
              <div key={svc.name} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <code className="text-sm font-semibold">{svc.name}</code>
                  <span className="text-xs text-gray-400">→ {svc.implementation}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${lt.color}`}>{lt.label}</span>
                  {svc.deps.length > 0 && (
                    <span className="text-xs text-gray-400">deps: {svc.deps.join(", ")}</span>
                  )}
                </div>
                <button onClick={() => onResolve?.(svc.name)}
                  className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">Resolve</button>
              </div>
            );
          })}
        </div>
      )}

      {tab === "graph" && (
        <div className="space-y-1 font-mono text-xs">
          {Object.entries(graph).map(([name, deps]) => (
            <div key={name} className="rounded-lg border dark:border-gray-700 p-2">
              <span className="font-bold">{name}</span>
              {deps.length > 0 ? (
                <span className="text-gray-400"> ← {deps.join(", ")}</span>
              ) : (
                <span className="text-gray-400"> (no deps)</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
