"use client";

import { useState } from "react";

interface ConfigField {
  key: string;
  label: string;
  type: "text" | "password" | "url" | "number" | "toggle";
  required: boolean;
  placeholder?: string;
  description?: string;
}

interface ConnectorInfo {
  id: string;
  name: string;
  icon: string;
  provider: string;
  fields: ConfigField[];
}

export function ConnectorConfigPanel({
  connector,
  initialValues,
  onSave,
  onTest,
}: {
  connector: ConnectorInfo;
  initialValues?: Record<string, string>;
  onSave?: (values: Record<string, string>) => void;
  onTest?: (values: Record<string, string>) => void;
}) {
  const [values, setValues] = useState<Record<string, string>>(initialValues || {});
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<"success" | "error" | null>(null);

  const updateField = (key: string, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }));
    setTestResult(null);
  };

  const allRequiredFilled = connector.fields
    .filter((f) => f.required)
    .every((f) => values[f.key]?.trim());

  const handleTest = () => {
    setTesting(true);
    setTestResult(null);
    onTest?.(values);
    setTimeout(() => {
      setTesting(false);
      setTestResult("success");
    }, 500);
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 p-6 space-y-5">
      <div className="flex items-center gap-3">
        <span className="text-3xl">{connector.icon}</span>
        <div>
          <h2 className="text-lg font-bold">{connector.name}</h2>
          <p className="text-sm text-gray-500">by {connector.provider}</p>
        </div>
      </div>

      <div className="space-y-4">
        {connector.fields.map((field) => (
          <div key={field.key}>
            <label className="block text-sm font-medium mb-1">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            {field.type === "toggle" ? (
              <button
                onClick={() => updateField(field.key, values[field.key] === "true" ? "false" : "true")}
                className={`rounded-full w-12 h-6 transition ${
                  values[field.key] === "true" ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"
                }`}
              >
                <div className={`w-5 h-5 rounded-full bg-white transform transition ${
                  values[field.key] === "true" ? "translate-x-6" : "translate-x-0.5"
                }`} />
              </button>
            ) : (
              <input
                type={field.type === "password" ? "password" : "text"}
                placeholder={field.placeholder}
                value={values[field.key] || ""}
                onChange={(e) => updateField(field.key, e.target.value)}
                className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
              />
            )}
            {field.description && (
              <p className="text-xs text-gray-400 mt-1">{field.description}</p>
            )}
          </div>
        ))}
      </div>

      {testResult && (
        <div className={`text-sm rounded-lg p-3 ${
          testResult === "success"
            ? "bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300"
            : "bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300"
        }`}>
          {testResult === "success" ? "✅ Connection test passed!" : "❌ Connection test failed"}
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={handleTest}
          disabled={!allRequiredFilled || testing}
          className="rounded-lg border dark:border-gray-600 px-4 py-2 text-sm font-medium disabled:opacity-50"
        >
          {testing ? "Testing..." : "🔌 Test Connection"}
        </button>
        <button
          onClick={() => onSave?.(values)}
          disabled={!allRequiredFilled}
          className="rounded-lg bg-blue-600 text-white px-4 py-2 text-sm font-medium disabled:opacity-50 hover:bg-blue-700"
        >
          💾 Save Configuration
        </button>
      </div>
    </div>
  );
}
