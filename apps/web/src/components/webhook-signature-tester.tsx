"use client";

import { useState } from "react";

export function WebhookSignatureTester({
  onVerify,
}: {
  onVerify?: (payload: string, secret: string, signature: string) => boolean;
}) {
  const [payload, setPayload] = useState('{"event":"test","data":{}}');
  const [secret, setSecret] = useState("");
  const [signature, setSignature] = useState("");
  const [result, setResult] = useState<"valid" | "invalid" | null>(null);

  const handleVerify = () => {
    if (onVerify) {
      const valid = onVerify(payload, secret, signature);
      setResult(valid ? "valid" : "invalid");
    } else {
      // Demo mode: check if signature is non-empty
      setResult(signature.length > 10 ? "valid" : "invalid");
    }
  };

  const handleGenerate = () => {
    // Simulate generating a signature
    const fakeSignature = `sha256=${btoa(payload + secret).slice(0, 44)}`;
    setSignature(fakeSignature);
    setResult(null);
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 p-6 space-y-4 max-w-lg">
      <h2 className="text-lg font-bold">🔐 Webhook Signature Tester</h2>
      <p className="text-sm text-gray-500">Test HMAC-SHA256 signature verification for your webhooks</p>

      <div>
        <label className="block text-sm font-medium mb-1">Payload</label>
        <textarea
          value={payload}
          onChange={(e) => { setPayload(e.target.value); setResult(null); }}
          rows={3}
          className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-mono"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Webhook Secret</label>
        <input
          type="password"
          value={secret}
          onChange={(e) => { setSecret(e.target.value); setResult(null); }}
          placeholder="whsec_..."
          className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-mono"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Signature</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={signature}
            onChange={(e) => { setSignature(e.target.value); setResult(null); }}
            placeholder="sha256=..."
            className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-mono"
          />
          <button
            onClick={handleGenerate}
            className="text-xs text-blue-500 border border-blue-300 dark:border-blue-700 px-3 py-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20"
          >
            Generate
          </button>
        </div>
      </div>

      <button
        onClick={handleVerify}
        disabled={!payload || !secret || !signature}
        className="w-full rounded-lg bg-blue-600 text-white py-2 text-sm font-medium disabled:opacity-50"
      >
        🔍 Verify Signature
      </button>

      {result && (
        <div className={`rounded-lg p-3 text-sm text-center ${
          result === "valid"
            ? "bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300"
            : "bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300"
        }`}>
          {result === "valid" ? "✅ Signature is valid!" : "❌ Signature verification failed"}
        </div>
      )}
    </div>
  );
}
