"use client";

import { useState } from "react";

interface SchemaField {
  name: string;
  type: string;
  required?: boolean;
  default?: unknown;
  description?: string;
  enum?: string[];
}

interface SchemaVersion {
  version: number;
  fieldCount: number;
  schemaId: string;
}

interface ValidationResult {
  valid: boolean;
  errors: string[];
  defaultsApplied: Record<string, unknown>;
  schemaVersion: number;
}

const typeColors: Record<string, string> = {
  string: "bg-green-100 text-green-700 dark:bg-green-900/30",
  integer: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  number: "bg-blue-100 text-blue-600 dark:bg-blue-900/30",
  boolean: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
  array: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  object: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
};

export function ConfigSchemaPanel({
  fields,
  versions,
  validationResult,
  onValidate,
  onSelectVersion,
}: {
  fields: SchemaField[];
  versions: SchemaVersion[];
  validationResult: ValidationResult | null;
  onValidate?: () => void;
  onSelectVersion?: (version: number) => void;
}) {
  const [tab, setTab] = useState<"schema" | "versions">("schema");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📐 Config Schema</h2>
        <button onClick={onValidate} className="text-sm bg-green-600 text-white px-3 py-1.5 rounded-lg">Validate</button>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("schema")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "schema" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Fields ({fields.length})
        </button>
        <button onClick={() => setTab("versions")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "versions" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Versions ({versions.length})
        </button>
      </div>

      {tab === "schema" && (
        <div className="space-y-1">
          {fields.map((f) => (
            <div key={f.name} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <code className="text-sm font-semibold">{f.name}</code>
                <span className={`text-xs px-1.5 py-0.5 rounded ${typeColors[f.type] || "bg-gray-100"}`}>{f.type}</span>
                {f.required && <span className="text-xs text-red-500">required</span>}
                {f.enum && <span className="text-xs text-gray-400">[{f.enum.join(", ")}]</span>}
              </div>
              {f.default !== undefined && (
                <span className="text-xs text-gray-500">default: {JSON.stringify(f.default)}</span>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === "versions" && (
        <div className="space-y-1">
          {versions.map((v) => (
            <div key={v.version} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50"
              onClick={() => onSelectVersion?.(v.version)}>
              <span className="text-sm font-bold">v{v.version}</span>
              <span className="text-xs text-gray-500">{v.fieldCount} fields</span>
            </div>
          ))}
        </div>
      )}

      {validationResult && (
        <div className={`rounded-lg border p-3 ${validationResult.valid ? "border-green-400 bg-green-50 dark:bg-green-900/10" : "border-red-400 bg-red-50 dark:bg-red-900/10"}`}>
          <span className={`text-sm font-bold ${validationResult.valid ? "text-green-600" : "text-red-600"}`}>
            {validationResult.valid ? "✅ Valid" : "❌ Invalid"}
          </span>
          {validationResult.errors.map((e, i) => (
            <div key={i} className="text-xs text-red-500 mt-0.5">{e}</div>
          ))}
        </div>
      )}
    </div>
  );
}
