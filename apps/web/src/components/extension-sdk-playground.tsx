"use client";

import { useState } from "react";

interface SDKMethod {
  name: string;
  description: string;
  category: string;
  params: { name: string; type: string; required: boolean }[];
  returnType: string;
  example: string;
}

export function ExtensionSDKPlayground({
  methods,
  onExecute,
}: {
  methods: SDKMethod[];
  onExecute?: (method: string, params: Record<string, string>) => void;
}) {
  const [selectedMethod, setSelectedMethod] = useState<string>(methods[0]?.name || "");
  const [params, setParams] = useState<Record<string, string>>({});
  const [output, setOutput] = useState<string>("");

  const method = methods.find((m) => m.name === selectedMethod);
  const categories = [...new Set(methods.map((m) => m.category))];

  const handleExecute = () => {
    if (method) {
      onExecute?.(method.name, params);
      setOutput(`// Response from ${method.name}\n${JSON.stringify({ ok: true, method: method.name, params }, null, 2)}`);
    }
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 border-b dark:border-gray-700">
        <h2 className="font-bold">🧪 SDK Playground</h2>
        <p className="text-xs text-gray-500">Test extension API methods interactively</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 divide-x dark:divide-gray-700">
        {/* Method list */}
        <div className="p-3 space-y-3 max-h-96 overflow-y-auto">
          {categories.map((cat) => (
            <div key={cat}>
              <div className="text-xs font-semibold text-gray-400 uppercase mb-1">{cat}</div>
              {methods.filter((m) => m.category === cat).map((m) => (
                <button
                  key={m.name}
                  onClick={() => { setSelectedMethod(m.name); setParams({}); setOutput(""); }}
                  className={`w-full text-left px-2 py-1.5 rounded text-sm ${
                    selectedMethod === m.name ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300" : "hover:bg-gray-100 dark:hover:bg-gray-800"
                  }`}
                >
                  <span className="font-mono text-xs">{m.name}</span>
                </button>
              ))}
            </div>
          ))}
        </div>

        {/* Parameters */}
        <div className="p-4 space-y-3">
          {method && (
            <>
              <div>
                <h3 className="font-semibold text-sm">{method.name}</h3>
                <p className="text-xs text-gray-500">{method.description}</p>
                <p className="text-xs text-gray-400 mt-1">Returns: <code>{method.returnType}</code></p>
              </div>
              {method.params.map((p) => (
                <div key={p.name}>
                  <label className="block text-xs font-medium mb-1">
                    {p.name} <span className="text-gray-400">({p.type})</span>
                    {p.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  <input
                    type="text"
                    value={params[p.name] || ""}
                    onChange={(e) => setParams({ ...params, [p.name]: e.target.value })}
                    className="w-full rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1.5 text-sm font-mono"
                    placeholder={p.type}
                  />
                </div>
              ))}
              <button
                onClick={handleExecute}
                className="w-full rounded-lg bg-green-600 text-white py-2 text-sm font-medium"
              >
                ▶ Execute
              </button>
            </>
          )}
        </div>

        {/* Output */}
        <div className="p-4">
          <div className="text-xs font-semibold text-gray-400 mb-2">Response</div>
          <pre className="bg-gray-900 text-green-400 text-xs p-3 rounded-lg overflow-auto max-h-64 font-mono">
            {output || "// Execute a method to see results"}
          </pre>
        </div>
      </div>
    </div>
  );
}
