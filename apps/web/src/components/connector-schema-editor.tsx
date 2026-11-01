"use client";

import { useState } from "react";

interface SchemaField {
  name: string;
  type: string;
  required: boolean;
  description?: string;
  default?: string;
  enumValues?: string[];
}

interface ValidationError {
  field: string;
  message: string;
}

const fieldTypes = ["string", "integer", "float", "boolean", "array", "object", "email", "url", "date"];

export function ConnectorSchemaEditor({
  fields,
  connectorName,
  errors,
  onAddField,
  onRemoveField,
  onValidate,
}: {
  fields: SchemaField[];
  connectorName: string;
  errors: ValidationError[];
  onAddField?: (field: SchemaField) => void;
  onRemoveField?: (name: string) => void;
  onValidate?: () => void;
}) {
  const [showAdd, setShowAdd] = useState(false);
  const [newName, setNewName] = useState("");
  const [newType, setNewType] = useState("string");
  const [newRequired, setNewRequired] = useState(true);

  const handleAdd = () => {
    if (newName.trim()) {
      onAddField?.({ name: newName.trim(), type: newType, required: newRequired });
      setNewName(""); setShowAdd(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔧 {connectorName} Schema</h2>
        <div className="flex gap-2">
          <button onClick={() => setShowAdd(!showAdd)}
            className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">+ Field</button>
          <button onClick={onValidate}
            className="text-sm bg-green-600 text-white px-3 py-1.5 rounded-lg">Validate</button>
        </div>
      </div>

      {showAdd && (
        <div className="rounded-lg border dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 flex gap-2 items-end">
          <div className="flex-1">
            <label className="text-xs text-gray-500 block">Name</label>
            <input type="text" value={newName} onChange={(e) => setNewName(e.target.value)}
              className="w-full rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm" />
          </div>
          <div>
            <label className="text-xs text-gray-500 block">Type</label>
            <select value={newType} onChange={(e) => setNewType(e.target.value)}
              className="rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm">
              {fieldTypes.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <label className="flex items-center gap-1 text-xs">
            <input type="checkbox" checked={newRequired} onChange={(e) => setNewRequired(e.target.checked)} />
            Required
          </label>
          <button onClick={handleAdd} className="text-sm bg-blue-600 text-white px-3 py-1 rounded">Add</button>
        </div>
      )}

      <div className="space-y-1">
        {fields.map((f) => {
          const hasError = errors.some((e) => e.field === f.name);
          return (
            <div key={f.name}
              className={`rounded-lg border p-3 flex items-center justify-between ${hasError ? "border-red-400 bg-red-50 dark:bg-red-900/10" : "dark:border-gray-700"}`}>
              <div className="flex items-center gap-3">
                <code className="text-sm font-semibold">{f.name}</code>
                <span className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{f.type}</span>
                {f.required && <span className="text-xs text-red-500">required</span>}
                {f.description && <span className="text-xs text-gray-400">{f.description}</span>}
              </div>
              <button onClick={() => onRemoveField?.(f.name)}
                className="text-xs text-red-500 hover:text-red-700">✕</button>
            </div>
          );
        })}
      </div>

      {errors.length > 0 && (
        <div className="space-y-1">
          {errors.map((e, i) => (
            <div key={i} className="text-xs text-red-500">⚠ {e.field}: {e.message}</div>
          ))}
        </div>
      )}
    </div>
  );
}
