"use client";

import { useState } from "react";

interface SchemaInfo { schemaId: string; endpoint: string; version: string; fields: number; direction: string; }

export default function SchemaRegistryCard() {
  const [schemas] = useState<SchemaInfo[]>([
    { schemaId: "s1", endpoint: "/api/users", version: "2.0", fields: 8, direction: "response" },
    { schemaId: "s2", endpoint: "/api/users", version: "2.0", fields: 5, direction: "request" },
    { schemaId: "s3", endpoint: "/api/orders", version: "1.0", fields: 12, direction: "response" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Schema Registry</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">API schema versioning with validation</p>

      <div className="mt-4 space-y-2">
        {schemas.map((s) => (
          <div key={s.schemaId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{s.endpoint}</span>
              <span className="ml-2 text-xs text-zinc-400">v{s.version} · {s.direction}</span>
            </div>
            <span className="text-xs text-zinc-500">{s.fields} fields</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{schemas.length} schemas registered</div>
    </div>
  );
}
