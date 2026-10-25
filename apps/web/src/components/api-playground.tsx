"use client";

import { useState } from "react";

interface ApiEndpoint {
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  path: string;
  description: string;
  params: { name: string; in: "path" | "query" | "body"; type: string; required: boolean }[];
}

export function ApiPlayground({
  endpoints,
  baseUrl,
  onExecute,
}: {
  endpoints: ApiEndpoint[];
  baseUrl: string;
  onExecute?: (method: string, url: string, body: object | null) => void;
}) {
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [paramValues, setParamValues] = useState<Record<string, string>>({});
  const [response, setResponse] = useState<string>("");
  const [status, setStatus] = useState<number>(0);

  const endpoint = endpoints[selectedIdx];
  const methodColors: Record<string, string> = {
    GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500",
    DELETE: "bg-red-500", PATCH: "bg-purple-500",
  };

  const buildUrl = () => {
    let url = `${baseUrl}${endpoint.path}`;
    const queryParams: string[] = [];
    for (const p of endpoint.params) {
      const val = paramValues[p.name] || "";
      if (p.in === "path") {
        url = url.replace(`{${p.name}}`, encodeURIComponent(val));
      } else if (p.in === "query" && val) {
        queryParams.push(`${p.name}=${encodeURIComponent(val)}`);
      }
    }
    if (queryParams.length) url += `?${queryParams.join("&")}`;
    return url;
  };

  const handleExecute = () => {
    const url = buildUrl();
    const bodyParams = endpoint.params.filter((p) => p.in === "body");
    const body = bodyParams.length > 0
      ? Object.fromEntries(bodyParams.map((p) => [p.name, paramValues[p.name] || ""]))
      : null;
    onExecute?.(endpoint.method, url, body);
    setStatus(200);
    setResponse(JSON.stringify({ ok: true, url, method: endpoint.method, body }, null, 2));
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 border-b dark:border-gray-700">
        <h2 className="font-bold">🧪 API Playground</h2>
        <p className="text-xs text-gray-500">{baseUrl}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 divide-x dark:divide-gray-700">
        {/* Endpoint list */}
        <div className="max-h-96 overflow-y-auto">
          {endpoints.map((ep, i) => (
            <button key={i} onClick={() => { setSelectedIdx(i); setParamValues({}); setResponse(""); }}
              className={`w-full text-left px-3 py-2 border-b dark:border-gray-800 text-sm ${
                i === selectedIdx ? "bg-blue-50 dark:bg-blue-900/10" : ""
              }`}>
              <span className={`inline-block text-white text-xs px-1.5 py-0.5 rounded font-mono mr-2 ${methodColors[ep.method]}`}>
                {ep.method}
              </span>
              <span className="font-mono text-xs">{ep.path}</span>
            </button>
          ))}
        </div>

        {/* Params */}
        <div className="p-4 space-y-3">
          <div className="text-sm font-medium">{endpoint?.description}</div>
          {endpoint?.params.map((p) => (
            <div key={p.name}>
              <label className="text-xs font-medium">
                {p.name} <span className="text-gray-400">({p.in}, {p.type})</span>
                {p.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              <input type="text" value={paramValues[p.name] || ""}
                onChange={(e) => setParamValues({ ...paramValues, [p.name]: e.target.value })}
                className="w-full mt-1 rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1.5 text-sm font-mono" />
            </div>
          ))}
          <button onClick={handleExecute}
            className="w-full rounded-lg bg-blue-600 text-white py-2 text-sm font-medium">
            ▶ Send Request
          </button>
        </div>

        {/* Response */}
        <div className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs text-gray-500">Response</span>
            {status > 0 && (
              <span className={`text-xs px-1.5 py-0.5 rounded ${status < 400 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                {status}
              </span>
            )}
          </div>
          <pre className="bg-gray-900 text-green-400 text-xs p-3 rounded-lg overflow-auto max-h-64 font-mono">
            {response || "// Send a request to see the response"}
          </pre>
        </div>
      </div>
    </div>
  );
}
