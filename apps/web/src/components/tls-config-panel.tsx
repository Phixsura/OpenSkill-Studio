"use client";

interface TlsConfigPanelProps { minVersion: string; grade: string; secure: boolean;
  cipherCount: number; weakCiphers: string[]; securePct: number; }

const GRADE_COLORS: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", F: "text-red-600" };

export function TlsConfigPanel({ minVersion, grade, secure, cipherCount, weakCiphers, securePct }: TlsConfigPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 TLS Configuration</h3>
        <div className="flex gap-2">
          <span className={`text-lg font-bold ${GRADE_COLORS[grade] ?? ""}`}>{grade}</span>
          <span className="text-xs text-gray-400 self-end">TLS {minVersion} · {cipherCount} ciphers · {securePct}%</span>
        </div>
      </div>
      {weakCiphers.length > 0 && (
        <div className="p-3 bg-red-50 dark:bg-red-900/10 text-xs text-red-600">
          ⚠ Weak ciphers: {weakCiphers.join(", ")}
        </div>
      )}
    </div>
  );
}
