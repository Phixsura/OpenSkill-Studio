"use client";

import { useState } from "react";

interface WebhookSecretCardProps { preview: string; createdAt: string; onRotate: () => void; onReveal: () => string; }

export function WebhookSecretCard({ preview, createdAt, onRotate, onReveal }: WebhookSecretCardProps) {
  const [revealed, setRevealed] = useState(false);
  const [secret, setSecret] = useState("");
  const [copied, setCopied] = useState(false);

  const reveal = () => {
    const s = onReveal();
    setSecret(s); setRevealed(true);
  };
  const copy = () => {
    navigator.clipboard?.writeText(secret); setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold">🔐 Webhook Secret</h3>
        <button onClick={onRotate} className="text-xs text-blue-600 hover:underline">Rotate</button>
      </div>
      <div className="flex items-center gap-2">
        <code className="flex-1 rounded bg-gray-100 px-3 py-2 text-xs font-mono dark:bg-gray-800">
          {revealed ? secret : preview}
        </code>
        {!revealed ? (
          <button onClick={reveal} className="text-xs text-blue-600">Reveal</button>
        ) : (
          <button onClick={copy} className="text-xs text-gray-400">{copied ? "✓" : "📋"}</button>
        )}
      </div>
      <p className="mt-1 text-xs text-gray-400">Created: {new Date(createdAt).toLocaleDateString()}</p>
    </div>
  );
}
