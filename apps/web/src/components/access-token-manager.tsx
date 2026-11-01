"use client";

interface Token { subject: string; scopes: string[]; expiresIn: number; }
interface AccessTokenManagerProps { tokens: Token[]; onIssue: () => void; onRevoke: (idx: number) => void; }

export function AccessTokenManager({ tokens, onIssue, onRevoke }: AccessTokenManagerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎫 Access Tokens</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{tokens.length} active</span>
          <button onClick={onIssue} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Issue</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tokens.map((t, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-sm font-medium">{t.subject}</div>
              <div className="text-[10px] text-gray-400">{t.scopes.join(", ")} · expires in {t.expiresIn}s</div>
            </div>
            <button onClick={() => onRevoke(i)} className="text-xs text-red-500 hover:underline">Revoke</button>
          </div>
        ))}
        {tokens.length === 0 && <div className="p-4 text-center text-sm text-gray-400">No active tokens</div>}
      </div>
    </div>
  );
}
