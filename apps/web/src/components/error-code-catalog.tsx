"use client";

import { useState } from "react";

interface ErrorEntry { code: number; name: string; message: string; httpStatus: number; category: string; machineCode: string; }
interface ErrorCodeCatalogProps { errors: ErrorEntry[]; categories: string[]; }

const statusColors: Record<string, string> = {
  "400": "text-yellow-600", "401": "text-orange-600", "403": "text-orange-600",
  "404": "text-blue-600", "429": "text-purple-600", "500": "text-red-600",
};

export function ErrorCodeCatalog({ errors, categories }: ErrorCodeCatalogProps) {
  const [filter, setFilter] = useState("ALL");
  const filtered = filter === "ALL" ? errors : errors.filter(e => e.category === filter);

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Error Codes</h3>
      <div className="flex gap-1 flex-wrap">
        <button onClick={() => setFilter("ALL")}
          className={`rounded px-2 py-0.5 text-xs ${filter === "ALL" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
        {categories.map(c => (
          <button key={c} onClick={() => setFilter(c)}
            className={`rounded px-2 py-0.5 text-xs ${filter === c ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{c}</button>
        ))}
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-72 overflow-y-auto">
        {filtered.map(e => (
          <div key={e.code} className="px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className="text-sm font-mono font-bold">{e.code}</span>
              <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{e.machineCode}</code>
              <span className={`text-xs font-medium ${statusColors[String(e.httpStatus)] ?? ""}`}>{e.httpStatus}</span>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">{e.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
