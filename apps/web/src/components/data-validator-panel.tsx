"use client";

import { useState } from "react";

interface ValidationError {
  path: string;
  message: string;
}

interface SchemaField {
  name: string;
  type: string;
  required: boolean;
  hasNested: boolean;
}

export function DataValidatorPanel({
  schema,
  errors,
  isValid,
  onValidate,
}: {
  schema: SchemaField[];
  errors: ValidationError[];
  isValid: boolean | null;
  onValidate?: () => void;
}) {
  const [tab, setTab] = useState<"schema" | "errors">("schema");

  const typeColors: Record<string, string> = {
    string: "bg-green-100 text-green-700 dark:bg-green-900/30",
    integer: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
    float: "bg-blue-100 text-blue-600 dark:bg-blue-900/30",
    boolean: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
    array: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
    object: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔍 Data Validator</h2>
        <div className="flex items-center gap-2">
          {isValid !== null && (
            <span className={`text-sm font-bold ${isValid ? "text-green-600" : "text-red-600"}`}>
              {isValid ? "✅ Valid" : `❌ ${errors.length} errors`}
            </span>
          )}
          <button onClick={onValidate} className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">Validate</button>
        </div>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("schema")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "schema" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Schema ({schema.length})
        </button>
        <button onClick={() => setTab("errors")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "errors" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Errors ({errors.length})
        </button>
      </div>

      {tab === "schema" && (
        <div className="space-y-1">
          {schema.map((f) => (
            <div key={f.name} className="rounded-lg border dark:border-gray-700 p-2 flex items-center gap-2">
              <code className="text-sm font-semibold">{f.name}</code>
              <span className={`text-xs px-1.5 py-0.5 rounded ${typeColors[f.type] || "bg-gray-100"}`}>{f.type}</span>
              {f.required && <span className="text-xs text-red-500">required</span>}
              {f.hasNested && <span className="text-xs text-purple-500">nested</span>}
            </div>
          ))}
        </div>
      )}

      {tab === "errors" && (
        <div className="space-y-1">
          {errors.length === 0 && <span className="text-sm text-gray-500">No errors</span>}
          {errors.map((e, i) => (
            <div key={i} className="rounded-lg border-l-4 border-red-400 bg-red-50 dark:bg-red-900/10 p-2">
              <code className="text-xs font-bold text-red-600">{e.path}</code>
              <span className="text-xs text-red-500 ml-2">{e.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
