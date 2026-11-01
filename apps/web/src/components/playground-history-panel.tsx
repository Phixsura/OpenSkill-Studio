"use client";

import { useState } from "react";

interface SavedReq { requestId: string; name: string; method: string; url: string; responseStatus: number; timestamp: string; }
interface Collection { collectionId: string; name: string; requestCount: number; }

const mc: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600" };

export function PlaygroundHistoryPanel({ requests, collections, onReplay, onDelete }: {
  requests: SavedReq[]; collections: Collection[];
  onReplay?: (id: string) => void; onDelete?: (id: string) => void;
}) {
  const [tab, setTab] = useState<"history" | "collections">("history");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📚 Playground History</h2>
      <div className="flex gap-1">
        <button onClick={() => setTab("history")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "history" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          History ({requests.length})
        </button>
        <button onClick={() => setTab("collections")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "collections" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Collections ({collections.length})
        </button>
      </div>

      {tab === "history" && (
        <div className="space-y-0.5">
          {requests.map((r) => (
            <div key={r.requestId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm">
                <span className={`font-bold text-xs w-12 ${mc[r.method] || ""}`}>{r.method}</span>
                <span>{r.name}</span>
                <code className="text-xs text-gray-400">{r.url}</code>
                {r.responseStatus > 0 && (
                  <span className={`text-xs ${r.responseStatus < 400 ? "text-green-600" : "text-red-600"}`}>{r.responseStatus}</span>
                )}
              </div>
              <div className="flex gap-1">
                <button onClick={() => onReplay?.(r.requestId)} className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">Replay</button>
                <button onClick={() => onDelete?.(r.requestId)} className="text-xs text-red-500">✕</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "collections" && (
        <div className="space-y-1">
          {collections.map((c) => (
            <div key={c.collectionId} className="rounded-lg border dark:border-gray-700 p-3">
              <span className="font-semibold text-sm">{c.name}</span>
              <span className="text-xs text-gray-400 ml-2">{c.requestCount} requests</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
