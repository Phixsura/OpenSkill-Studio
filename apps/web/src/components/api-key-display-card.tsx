"use client";
import { useState } from "react";

interface ApiKeyDisplayCardProps { name: string; masked: string; fullKey: string;
  scopes: string[]; lastUsed: string; onRevoke: () => void; }

export function ApiKeyDisplayCard({ name, masked, fullKey, scopes, lastUsed, onRevoke }: ApiKeyDisplayCardProps) {
  const [revealed, setRevealed] = useState(false);
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard?.writeText(fullKey).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000); });
  };
  return (
    <div className="rounded-xl border dark:border-gray-700 p-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold">{name}</h4>
        <button onClick={onRevoke} className="text-xs text-red-500 hover:text-red-700">Revoke</button>
      </div>
      <div className="flex items-center gap-2 bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 mb-2">
        <code className="text-xs font-mono flex-1">{revealed ? fullKey : masked}</code>
        <button onClick={() => setRevealed(!revealed)} className="text-xs text-gray-400">{revealed ? "🙈" : "👁️"}</button>
        <button onClick={handleCopy} className="text-xs text-blue-600">{copied ? "✓" : "📋"}</button>
      </div>
      <div className="flex items-center justify-between text-xs text-gray-400">
        <div className="flex gap-1">{scopes.map(s => <span key={s} className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">{s}</span>)}</div>
        <span>Last used: {lastUsed}</span>
      </div>
    </div>
  );
}
