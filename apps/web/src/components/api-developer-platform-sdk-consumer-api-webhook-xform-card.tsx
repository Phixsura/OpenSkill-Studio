"use client";

import { useState } from "react";

interface PipelineInfo { id: string; ops: string[]; transforms: number; }

export default function WebhookTransformerCard() {
  const [pipelines] = useState<PipelineInfo[]>([
    { id: "p-orders", ops: ["rename", "remove", "add"], transforms: 1250 },
    { id: "p-users", ops: ["flatten", "wrap"], transforms: 890 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Transformer</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Payload transformation pipeline</p>

      <div className="mt-4 space-y-2">
        {pipelines.map((p) => (
          <div key={p.id} className="rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center justify-between">
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{p.id}</span>
              <span className="text-xs text-zinc-400">{p.transforms.toLocaleString()} runs</span>
            </div>
            <div className="mt-1 flex gap-1">
              {p.ops.map((op) => (
                <span key={op} className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">{op}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{pipelines.length} pipelines</div>
    </div>
  );
}
