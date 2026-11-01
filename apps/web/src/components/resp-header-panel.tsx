"use client";
interface HeaderIssue { header: string; issue: string; }
interface RespHeaderPanelProps { headersCount: number; issues: HeaderIssue[]; secure: boolean; valid: boolean; }
export function RespHeaderPanel({ headersCount, issues, secure, valid }: RespHeaderPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Response Headers</h3>
        <span className={`text-xs font-bold ${valid ? "text-green-600" : "text-yellow-600"}`}>
          {headersCount} headers · {secure ? "🔒 Secure" : "⚠ Issues"}{issues.length > 0 ? ` · ${issues.length} issues` : ""}
        </span>
      </div>
      {issues.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {issues.map((i, idx) => (
            <div key={idx} className="px-4 py-1.5 text-xs text-yellow-600">
              <span className="font-mono">{i.header}</span>: {i.issue}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
