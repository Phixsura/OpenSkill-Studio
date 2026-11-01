"use client";

import { useState } from "react";

interface ClientCredentialsFormProps {
  clientId: string;
  clientSecret?: string;
  onRegenerate: () => void;
}

export function ClientCredentialsForm({ clientId, clientSecret, onRegenerate }: ClientCredentialsFormProps) {
  const [showSecret, setShowSecret] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  const copy = (text: string, label: string) => {
    navigator.clipboard?.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="font-semibold">OAuth Credentials</h4>
      <div>
        <label className="text-xs text-gray-500">Client ID</label>
        <div className="flex items-center gap-2">
          <code className="flex-1 rounded bg-gray-100 px-2 py-1 text-sm dark:bg-gray-800">{clientId}</code>
          <button onClick={() => copy(clientId, "id")} className="text-xs text-blue-600">{copied === "id" ? "✅" : "Copy"}</button>
        </div>
      </div>
      {clientSecret && (
        <div>
          <label className="text-xs text-gray-500">Client Secret</label>
          <div className="flex items-center gap-2">
            <code className="flex-1 rounded bg-gray-100 px-2 py-1 text-sm dark:bg-gray-800">
              {showSecret ? clientSecret : "••••••••••••••••"}
            </code>
            <button onClick={() => setShowSecret(!showSecret)} className="text-xs text-gray-600">{showSecret ? "Hide" : "Show"}</button>
            <button onClick={() => copy(clientSecret, "secret")} className="text-xs text-blue-600">{copied === "secret" ? "✅" : "Copy"}</button>
          </div>
          <p className="mt-1 text-xs text-yellow-600">⚠️ Secret shown once only. Save it now.</p>
        </div>
      )}
      <button onClick={onRegenerate} className="text-xs text-red-500 hover:text-red-700">Regenerate credentials</button>
    </div>
  );
}
