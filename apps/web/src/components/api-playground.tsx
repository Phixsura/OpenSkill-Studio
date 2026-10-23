"use client";

import { useState } from "react";

interface ApiPlaygroundProps { onSend: (method: string, url: string) => void; }

const methods = ["GET", "POST", "PUT", "DELETE"];
const methodColors: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500", DELETE: "bg-red-500",
};

export function ApiPlayground({ onSend }: ApiPlaygroundProps) {
  const [method, setMethod] = useState("GET");
  const [url, setUrl] = useState("");

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">API Playground</h3>
      <div className="flex gap-2">
        <select value={method} onChange={e => setMethod(e.target.value)}
          className={`rounded px-2 py-2 text-sm text-white font-medium ${methodColors[method] ?? "bg-gray-500"}`}>
          {methods.map(m => <option key={m} value={m}>{m}</option>)}
        </select>
        <input type="url" value={url} onChange={e => setUrl(e.target.value)}
          placeholder="https://api.example.com/v1/apps"
          className="flex-1 rounded border px-3 py-2 text-sm font-mono dark:bg-gray-800 dark:border-gray-600" />
        <button onClick={() => url && onSend(method, url)}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white font-medium">Send</button>
      </div>
    </div>
  );
}
