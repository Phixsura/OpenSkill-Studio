"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface ManifestEditorProps {
  initialValue?: Record<string, unknown>;
  onSave?: (manifest: Record<string, unknown>) => void;
  readOnly?: boolean;
}

const DEFAULT_MANIFEST = {
  schema_version: "1.0",
  app: {
    name: "",
    slug: "",
    version: "1.0.0",
    category: "connector",
  },
  permissions: [] as string[],
  sandbox: {
    runtime: "nodejs20",
    memory_mb: 128,
    timeout_seconds: 30,
    network: {
      allowed_hosts: [] as string[],
      egress_policy: "allowlist",
    },
  },
  event_subscriptions: [] as string[],
  secrets: [] as Array<{ key: string; description: string; required: boolean }>,
};

/**
 * ManifestEditor — visual editor for app manifest.json files.
 * Includes inline validation against the platform schema.
 */
export function ManifestEditor({
  initialValue,
  onSave,
  readOnly = false,
}: ManifestEditorProps) {
  const [json, setJson] = useState(
    JSON.stringify(initialValue ?? DEFAULT_MANIFEST, null, 2),
  );
  const [parseError, setParseError] = useState("");
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    errors: string[];
    warnings: string[];
  } | null>(null);

  const validateMutation = useMutation({
    mutationFn: async (manifest: Record<string, unknown>) => {
      const r = await apiWithAuth<{
        data: { valid: boolean; errors: string[]; warnings: string[] };
      }>("/developer/validate-manifest", {
        method: "POST",
        body: JSON.stringify({ manifest }),
      });
      return r.data;
    },
    onSuccess: (data) => {
      setValidationResult(data);
    },
  });

  const handleValidate = () => {
    try {
      const parsed = JSON.parse(json);
      setParseError("");
      validateMutation.mutate(parsed);
    } catch {
      setParseError("Invalid JSON");
      setValidationResult(null);
    }
  };

  const handleSave = () => {
    try {
      const parsed = JSON.parse(json);
      setParseError("");
      onSave?.(parsed);
    } catch {
      setParseError("Invalid JSON — cannot save");
    }
  };

  const handleFormat = () => {
    try {
      const parsed = JSON.parse(json);
      setJson(JSON.stringify(parsed, null, 2));
      setParseError("");
    } catch {
      setParseError("Cannot format — invalid JSON");
    }
  };

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center gap-2">
        <Button size="sm" variant="outline" onClick={handleValidate} disabled={validateMutation.isPending}>
          {validateMutation.isPending ? "Validating…" : "✓ Validate"}
        </Button>
        <Button size="sm" variant="outline" onClick={handleFormat}>
          Format JSON
        </Button>
        {onSave && !readOnly && (
          <Button size="sm" onClick={handleSave}>
            Save Manifest
          </Button>
        )}
      </div>

      {/* Editor */}
      <textarea
        className="w-full rounded-lg border bg-gray-900 p-4 font-mono text-sm text-gray-100 dark:border-gray-600"
        value={json}
        onChange={(e) => {
          setJson(e.target.value);
          setParseError("");
          setValidationResult(null);
        }}
        rows={20}
        readOnly={readOnly}
        spellCheck={false}
      />

      {/* Parse error */}
      {parseError && <p className="text-sm text-red-600">⚠️ {parseError}</p>}

      {/* Validation result */}
      {validationResult && (
        <div
          className={`rounded-lg border p-4 ${
            validationResult.valid
              ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20"
              : "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20"
          }`}
        >
          <p className="mb-2 font-medium">
            {validationResult.valid ? "✅ Manifest is valid" : "❌ Validation failed"}
          </p>
          {validationResult.errors.length > 0 && (
            <ul className="mb-2 list-inside list-disc space-y-1 text-sm text-red-700 dark:text-red-400">
              {validationResult.errors.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          )}
          {validationResult.warnings.length > 0 && (
            <ul className="list-inside list-disc space-y-1 text-sm text-yellow-700 dark:text-yellow-400">
              {validationResult.warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
