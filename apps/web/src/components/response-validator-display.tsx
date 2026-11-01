"use client";

interface ResponseValidatorDisplayProps { valid: boolean; errors: string[];
  responseType: string; statusCode: number; statusIssues: string[]; }

export function ResponseValidatorDisplay({ valid, errors, responseType, statusCode, statusIssues }: ResponseValidatorDisplayProps) {
  const allIssues = [...errors, ...statusIssues];
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">✅ Response Validator</h3>
        <div className="flex items-center gap-2">
          <span className={`text-xs px-2 py-0.5 rounded ${statusCode < 400 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{statusCode}</span>
          <span className="text-xs text-gray-400 capitalize">{responseType}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${valid && statusIssues.length === 0 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {allIssues.length === 0 ? "✅ Valid" : `❌ ${allIssues.length} issues`}
          </span>
        </div>
      </div>
      {allIssues.length > 0 && (
        <div className="space-y-1">
          {allIssues.map((e, i) => (
            <p key={i} className="text-xs text-red-500">• {e}</p>
          ))}
        </div>
      )}
    </div>
  );
}
