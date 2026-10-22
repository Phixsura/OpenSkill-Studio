"use client";

interface LintResult { level: string; field: string; message: string; }

interface ManifestLintResultsProps { results: LintResult[]; }

const LEVEL_ICONS: Record<string, string> = { warning: "⚠️", info: "💡", error: "❌" };

export function ManifestLintResults({ results }: ManifestLintResultsProps) {
  if (results.length === 0) return <p className="py-3 text-center text-sm text-green-600">✅ No suggestions — manifest looks great!</p>;
  return (
    <div className="space-y-2">
      <p className="text-sm text-gray-500">{results.length} suggestion{results.length !== 1 ? "s" : ""}</p>
      {results.map((r, i) => (
        <div key={i} className="flex items-start gap-2 rounded border border-gray-200 p-3 text-sm dark:border-gray-700">
          <span>{LEVEL_ICONS[r.level] ?? "•"}</span>
          <div>
            <code className="text-xs text-gray-500">{r.field}</code>
            <p>{r.message}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
