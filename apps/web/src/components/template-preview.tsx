"use client";

interface TemplatePreviewProps { template: string; output: string; missing: string[]; hasMissing: boolean; }

export function TemplatePreview({ template, output, missing, hasMissing }: TemplatePreviewProps) {
  return (
    <div className="space-y-3">
      <div>
        <p className="text-xs font-semibold text-gray-400 mb-1">Template</p>
        <pre className="rounded bg-gray-100 p-3 text-sm font-mono dark:bg-gray-800 overflow-x-auto">{template}</pre>
      </div>
      <div>
        <p className="text-xs font-semibold text-gray-400 mb-1">Output</p>
        <div className="rounded border p-3 text-sm dark:border-gray-700">{output}</div>
      </div>
      {hasMissing && (
        <div className="flex items-center gap-2 text-xs text-yellow-600">
          <span>⚠</span>
          <span>Missing variables: {missing.join(", ")}</span>
        </div>
      )}
    </div>
  );
}
