"use client";

interface TokenInfo { preview: string; subject: string; scopes: string[]; expiresIn: number; }
interface AccessTokenPanelProps { tokens: TokenInfo[]; activeCount: number; revokedCount: number; }

export function AccessTokenPanel({ tokens, activeCount, revokedCount }: AccessTokenPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎫 Access Tokens</h3>
        <span className="text-xs text-gray-400">{activeCount} active · {revokedCount} revoked</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tokens.map(t => (
          <div key={t.preview} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono">{t.preview}</span>
              <span className="text-gray-400">{t.expiresIn}s left</span>
            </div>
            <div className="text-gray-400">{t.subject} · {t.scopes.join(", ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
