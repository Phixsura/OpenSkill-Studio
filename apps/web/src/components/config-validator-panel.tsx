"use client";

interface ValidationResult { valid: boolean; issues: string[]; }

export function ConfigValidatorPanel({ result, onValidate }: {
  result: ValidationResult | null; onValidate?: (json: string) => void;
}) {
  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">Config Validator</h3>
      <textarea placeholder='Paste your extension.json here...' rows={6}
        className="w-full border dark:border-gray-700 rounded-lg px-3 py-2 text-xs bg-transparent font-mono resize-none"
        onBlur={e => onValidate?.(e.target.value)} />
      {result && (
        <div className={`rounded-xl p-3 ${result.valid ? "bg-green-50 border border-green-200 dark:bg-green-900/10 dark:border-green-800" : "bg-red-50 border border-red-200 dark:bg-red-900/10 dark:border-red-800"}`}>
          <div className="flex items-center gap-2 mb-1">
            <span>{result.valid ? "✅" : "❌"}</span>
            <span className="font-medium text-sm">{result.valid ? "Valid configuration" : "Invalid configuration"}</span>
          </div>
          {result.issues.length > 0 && (
            <ul className="text-xs space-y-0.5 ml-6">
              {result.issues.map((issue, i) => (
                <li key={i} className={issue.startsWith("[warn]") ? "text-yellow-600" : "text-red-600"}>
                  {issue}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
