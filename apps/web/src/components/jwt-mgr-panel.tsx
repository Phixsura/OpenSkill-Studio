"use client";
interface JwtInfo { subject: string; expiresIn: number; claims: string[]; }
interface JwtMgrPanelProps { tokens: JwtInfo[]; activeCount: number; }
export function JwtMgrPanel({ tokens, activeCount }: JwtMgrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎫 JWT Tokens</h3>
        <span className="text-xs text-gray-400">{activeCount} active</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tokens.map(t => (
          <div key={t.subject} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{t.subject}</span>
            <span className="text-gray-400">{t.expiresIn}s · {t.claims.join(", ")}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
