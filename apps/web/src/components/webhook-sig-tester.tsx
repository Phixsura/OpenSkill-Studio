"use client";

import { useState } from "react";

interface WebhookSigTesterProps { onSign: (payload: string) => void;
  onVerify: (payload: string, header: string) => void;
  result: { valid?: boolean; error?: string; signature?: string } | null; }

export function WebhookSigTester({ onSign, onVerify, result }: WebhookSigTesterProps) {
  const [payload, setPayload] = useState("");
  const [header, setHeader] = useState("");
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔏 Webhook Signatures</h3>
      </div>
      <div className="p-4 space-y-3">
        <div>
          <label className="text-xs text-gray-400">Payload</label>
          <textarea value={payload} onChange={e => setPayload(e.target.value)} rows={3}
            className="w-full mt-1 px-3 py-2 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-600 font-mono" />
        </div>
        <div>
          <label className="text-xs text-gray-400">Signature Header (for verify)</label>
          <input value={header} onChange={e => setHeader(e.target.value)}
            className="w-full mt-1 px-3 py-2 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-600 font-mono" />
        </div>
        <div className="flex gap-2">
          <button onClick={() => onSign(payload)} className="px-3 py-1.5 text-xs bg-blue-500 text-white rounded-lg">Sign</button>
          <button onClick={() => onVerify(payload, header)} className="px-3 py-1.5 text-xs bg-green-500 text-white rounded-lg">Verify</button>
        </div>
        {result && (
          <div className={`p-3 rounded-lg text-xs ${result.valid ? "bg-green-50 text-green-700 dark:bg-green-900/10" : result.error ? "bg-red-50 text-red-700 dark:bg-red-900/10" : "bg-blue-50 text-blue-700 dark:bg-blue-900/10"}`}>
            {result.valid !== undefined ? (result.valid ? "✅ Valid" : `❌ ${result.error}`) : null}
            {result.signature && <div className="font-mono mt-1 break-all">{result.signature}</div>}
          </div>
        )}
      </div>
    </div>
  );
}
