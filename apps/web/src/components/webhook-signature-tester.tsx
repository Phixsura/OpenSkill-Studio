"use client";

import { useState } from "react";

interface WebhookSignatureTesterProps { onVerify: (payload: string, signature: string, secret: string) => { valid: boolean; error?: string }; }

export function WebhookSignatureTester({ onVerify }: WebhookSignatureTesterProps) {
  const [payload, setPayload] = useState('{"event":"test"}');
  const [signature, setSignature] = useState("");
  const [secret, setSecret] = useState("");
  const [result, setResult] = useState<{ valid: boolean; error?: string } | null>(null);

  const verify = () => setResult(onVerify(payload, signature, secret));

  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <h2 className="text-lg font-semibold">Signature Tester</h2>
      <div className="space-y-2">
        <div>
          <label className="text-xs text-gray-400">Payload</label>
          <textarea value={payload} onChange={e => setPayload(e.target.value)} rows={2}
            className="w-full rounded border px-3 py-1.5 font-mono text-xs dark:border-gray-600 dark:bg-gray-700" />
        </div>
        <div>
          <label className="text-xs text-gray-400">Signature Header</label>
          <input value={signature} onChange={e => setSignature(e.target.value)}
            className="w-full rounded border px-3 py-1.5 font-mono text-xs dark:border-gray-600 dark:bg-gray-700" />
        </div>
        <div>
          <label className="text-xs text-gray-400">Secret</label>
          <input value={secret} onChange={e => setSecret(e.target.value)} type="password"
            className="w-full rounded border px-3 py-1.5 font-mono text-xs dark:border-gray-600 dark:bg-gray-700" />
        </div>
      </div>
      <button onClick={verify} className="w-full rounded bg-blue-600 py-2 text-sm text-white">Verify</button>
      {result && (
        <div className={`rounded p-2 text-center text-sm ${result.valid ? "bg-green-50 text-green-700 dark:bg-green-900/10" : "bg-red-50 text-red-700 dark:bg-red-900/10"}`}>
          {result.valid ? "✅ Valid signature" : `❌ ${result.error}`}
        </div>
      )}
    </div>
  );
}
