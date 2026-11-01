"use client";

interface TokenIntrospectViewerProps { active: boolean; expired: boolean;
  subject: string; issuer: string; scopes: string[]; tokenType: string;
  authorized: boolean; missingScopes: string[]; }

export function TokenIntrospectViewer({ active, expired, subject, issuer, scopes, tokenType, authorized, missingScopes }: TokenIntrospectViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 Token Introspection</h3>
        <div className="flex gap-2 text-xs">
          <span className={active ? "text-green-600" : "text-red-500"}>{active ? "✅ Active" : "❌ Inactive"}</span>
          {expired && <span className="text-red-500">⏰ Expired</span>}
        </div>
      </div>
      <div className="p-3 space-y-1 text-xs">
        <div><span className="text-gray-400">Subject:</span> <span className="font-mono">{subject}</span></div>
        <div><span className="text-gray-400">Issuer:</span> {issuer}</div>
        <div><span className="text-gray-400">Type:</span> {tokenType}</div>
        <div className="flex gap-1 flex-wrap mt-1">
          {scopes.map(s => <span key={s} className="px-1.5 py-0.5 text-[10px] bg-blue-100 dark:bg-blue-900/20 rounded">{s}</span>)}
        </div>
      </div>
      {missingScopes.length > 0 && (
        <div className="px-3 py-2 border-t dark:border-gray-700 text-xs text-red-500">
          Missing: {missingScopes.join(", ")}
        </div>
      )}
    </div>
  );
}
