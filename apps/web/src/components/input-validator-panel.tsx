"use client";

import { useState } from "react";

interface ValidationError {
  field: string;
  message: string;
  rule: string;
}

interface ValidationRule {
  field: string;
  rule: string;
  value?: unknown;
}

const ruleIcons: Record<string, string> = {
  required: "❗", type: "🔤", min: "⬇️", max: "⬆️",
  minlen: "📏", maxlen: "📐", pattern: "🔣", enum: "📋",
};

export function InputValidatorPanel({
  rules,
  errors,
  isValid,
  xssDetected,
  onValidate,
  onSanitize,
}: {
  rules: ValidationRule[];
  errors: ValidationError[];
  isValid: boolean | null;
  xssDetected: boolean;
  onValidate?: () => void;
  onSanitize?: () => void;
}) {
  const [tab, setTab] = useState<"rules" | "errors">("rules");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">✅ Input Validator</h2>
        <div className="flex items-center gap-2">
          {isValid !== null && (
            <span className={`text-sm font-bold ${isValid ? "text-green-600" : "text-red-600"}`}>
              {isValid ? "✅ Valid" : "❌ Invalid"}
            </span>
          )}
          {xssDetected && <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">⚠ XSS</span>}
          <button onClick={onValidate} className="text-xs bg-blue-600 text-white px-3 py-1 rounded-lg">Validate</button>
          <button onClick={onSanitize} className="text-xs bg-yellow-600 text-white px-3 py-1 rounded-lg">Sanitize</button>
        </div>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("rules")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "rules" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Rules ({rules.length})
        </button>
        <button onClick={() => setTab("errors")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "errors" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Errors ({errors.length})
        </button>
      </div>

      {tab === "rules" && (
        <div className="space-y-1">
          {rules.map((r, i) => (
            <div key={i} className="rounded-lg border dark:border-gray-700 p-2 flex items-center gap-2 text-sm">
              <span>{ruleIcons[r.rule] || "📌"}</span>
              <code className="font-semibold">{r.field}</code>
              <span className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{r.rule}</span>
              {r.value !== undefined && <span className="text-xs text-gray-400">{JSON.stringify(r.value)}</span>}
            </div>
          ))}
        </div>
      )}

      {tab === "errors" && (
        <div className="space-y-1">
          {errors.length === 0 && <span className="text-sm text-gray-500">No validation errors</span>}
          {errors.map((e, i) => (
            <div key={i} className="rounded-lg border-l-4 border-red-400 bg-red-50 dark:bg-red-900/10 p-2">
              <div className="flex items-center gap-2 text-sm">
                <code className="font-semibold text-red-600">{e.field}</code>
                <span className="text-xs text-gray-400">[{e.rule}]</span>
              </div>
              <span className="text-xs text-red-500">{e.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
