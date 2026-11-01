"use client";

import { useState } from "react";

interface TwoFactorSetupProps { qrUri: string; recoveryCodes: string[];
  onVerify: (code: string) => boolean; onComplete: () => void; }

export function TwoFactorSetup({ qrUri, recoveryCodes, onVerify, onComplete }: TwoFactorSetupProps) {
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"scan" | "verify" | "recovery">("scan");
  const [error, setError] = useState("");

  const verify = () => {
    if (onVerify(code)) { setStep("recovery"); setError(""); }
    else setError("Invalid code");
  };

  return (
    <div className="mx-auto max-w-sm space-y-4">
      <h2 className="text-lg font-bold">🔐 Two-Factor Authentication</h2>
      {step === "scan" && (
        <>
          <p className="text-sm text-gray-500">Scan this QR code with your authenticator app</p>
          <div className="rounded-lg border p-4 text-center dark:border-gray-700">
            <code className="text-xs break-all text-gray-400">{qrUri}</code>
          </div>
          <button onClick={() => setStep("verify")} className="w-full rounded bg-blue-600 py-2 text-sm text-white">Next</button>
        </>
      )}
      {step === "verify" && (
        <>
          <p className="text-sm text-gray-500">Enter the 6-digit code from your authenticator</p>
          <input value={code} onChange={e => setCode(e.target.value)} maxLength={6}
            placeholder="000000" className="w-full rounded border px-3 py-2 text-center text-lg font-mono tracking-widest dark:bg-gray-800 dark:border-gray-600" />
          {error && <p className="text-xs text-red-500">{error}</p>}
          <button onClick={verify} className="w-full rounded bg-blue-600 py-2 text-sm text-white">Verify</button>
        </>
      )}
      {step === "recovery" && (
        <>
          <p className="text-sm text-gray-500">Save these recovery codes in a safe place</p>
          <div className="grid grid-cols-2 gap-1 rounded-lg bg-gray-100 p-3 dark:bg-gray-800">
            {recoveryCodes.map(c => <code key={c} className="text-xs font-mono">{c}</code>)}
          </div>
          <button onClick={onComplete} className="w-full rounded bg-green-600 py-2 text-sm text-white">Done</button>
        </>
      )}
    </div>
  );
}
