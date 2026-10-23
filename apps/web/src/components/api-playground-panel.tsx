"use client";
import { useState } from "react";

interface ApiPlaygroundPanelProps {
  baseUrl: string;
  onSend: (method: string, path: string, body: string) => void;
  response: { status: number; body: unknown } | null;
}

const METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"];
const METHOD_COLOR: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  PATCH: "text-orange-600", DELETE: "text-red-600",
};

export function ApiPlaygroundPanel({ baseUrl, onSend, response }: ApiPlaygroundPanelProps) {
  const [method, setMethod] = useState("GET");
  const [path, setPath] = useState("/api/v1/");
  const [body, setBody] = useState("");

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🧪 API Playground</h3>
        <p className="text-xs text-gray-400">{baseUrl}</p>
      </div>
      <div className="p-4 space-y-3">
        <div className="flex gap-2">
          <select value={method} onChange={e => setMethod(e.target.value)}
            className={`px-2 py-1.5 border rounded text-sm font-bold dark:bg-gray-800 dark:border-gray-600 ${METHOD_COLOR[method] || ""}`}>
            {METHODS.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
          <input value={path} onChange={e => setPath(e.target.value)}
            className="flex-1 px-2 py-1.5 border rounded text-sm font-mono dark:bg-gray-800 dark:border-gray-600" />
          <button onClick={() => onSend(method, path, body)}
            className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded font-medium hover:bg-blue-700">Send</button>
        </div>
        {["POST", "PUT", "PATCH"].includes(method) && (
          <textarea value={body} onChange={e => setBody(e.target.value)} rows={4} placeholder='{"key": "value"}'
            className="w-full px-3 py-2 border rounded text-xs font-mono dark:bg-gray-800 dark:border-gray-600" />
        )}
        {response && (
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <span className={`text-sm font-bold ${response.status < 300 ? "text-green-600" : "text-red-600"}`}>
                {response.status}
              </span>
            </div>
            <pre className="text-xs overflow-auto max-h-48">{JSON.stringify(response.body, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
