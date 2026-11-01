"use client";

import { useState } from "react";

interface TransformStep {
  id: string;
  name: string;
  kind: string;
  enabled: boolean;
}

export default function TransformPipelineCard() {
  const [steps] = useState<TransformStep[]>([
    { id: "t1", name: "Rename user_id", kind: "rename_field", enabled: true },
    { id: "t2", name: "Remove internal", kind: "remove_field", enabled: true },
    { id: "t3", name: "Add version", kind: "add_field", enabled: true },
    { id: "t4", name: "Map status codes", kind: "map_value", enabled: false },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Transform Pipeline
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Chainable request/response transforms
      </p>

      <div className="mt-4 space-y-2">
        {steps.map((s, i) => (
          <div
            key={s.id}
            className={`flex items-center gap-2 rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700 ${!s.enabled ? "opacity-50" : ""}`}
          >
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-zinc-200 text-xs font-bold text-zinc-600 dark:bg-zinc-700 dark:text-zinc-300">
              {i + 1}
            </span>
            <span className="text-sm text-zinc-800 dark:text-zinc-200">{s.name}</span>
            <span className="ml-auto rounded bg-zinc-100 px-1.5 py-0.5 text-xs text-zinc-500 dark:bg-zinc-800">
              {s.kind}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {steps.filter((s) => s.enabled).length}/{steps.length} steps active
      </div>
    </div>
  );
}
