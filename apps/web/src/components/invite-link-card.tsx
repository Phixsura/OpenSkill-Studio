"use client";
import { useState } from "react";

interface InviteLinkCardProps { url: string; code: string; role: string;
  maxUses: number | string; uses: number; onRevoke: (code: string) => void; }

export function InviteLinkCard({ url, code, role, maxUses, uses, onRevoke }: InviteLinkCardProps) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard?.writeText(url).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000); });
  };
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold">🔗 Invite Link</h4>
        <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 capitalize">{role}</span>
      </div>
      <div className="flex items-center gap-2 mb-3">
        <input readOnly value={url} className="flex-1 text-xs font-mono px-2 py-1.5 border rounded bg-gray-50 dark:bg-gray-800 dark:border-gray-600" />
        <button onClick={handleCopy}
          className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">
          {copied ? "✅ Copied" : "Copy"}
        </button>
      </div>
      <div className="flex items-center justify-between text-xs text-gray-400">
        <span>{uses} / {maxUses === "unlimited" ? "∞" : maxUses} uses</span>
        <button onClick={() => onRevoke(code)}
          className="text-red-500 hover:text-red-700">Revoke</button>
      </div>
    </div>
  );
}
