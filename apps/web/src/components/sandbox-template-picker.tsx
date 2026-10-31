"use client";
import { useState } from "react";

interface Template { templateId: string; name: string; runtime: string; description: string; category: string; }

const runtimeIcons: Record<string, string> = { python: "🐍", node: "🟢", deno: "🦕", go: "🔵" };

export function SandboxTemplatePicker({ templates, onSelect }: { templates: Template[]; onSelect?: (id: string) => void }) {
  const [runtime, setRuntime] = useState("");
  const runtimes = [...new Set(templates.map(t => t.runtime))];
  const filtered = runtime ? templates.filter(t => t.runtime === runtime) : templates;

  return (
    <div className="space-y-3">
      <div className="flex gap-1">
        <button onClick={() => setRuntime("")} className={`text-xs px-3 py-1 rounded-full ${!runtime ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
        {runtimes.map(r => (
          <button key={r} onClick={() => setRuntime(r)} className={`text-xs px-3 py-1 rounded-full ${runtime === r ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {runtimeIcons[r] || "📦"} {r}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {filtered.map(t => (
          <button key={t.templateId} onClick={() => onSelect?.(t.templateId)}
            className="text-left border dark:border-gray-700 rounded-xl p-3 hover:border-blue-400 transition-colors">
            <div className="flex items-center gap-2">
              <span className="text-xl">{runtimeIcons[t.runtime] || "📦"}</span>
              <div>
                <span className="font-medium text-sm block">{t.name}</span>
                <span className="text-xs text-gray-500">{t.description || t.category}</span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
