"use client";

interface ConfigEncryptionStatusProps { totalFields: number; encryptedFields: number;
  unencryptedSensitive: string[]; onEncrypt: (field: string) => void; }

export function ConfigEncryptionStatus({ totalFields, encryptedFields, unencryptedSensitive, onEncrypt }: ConfigEncryptionStatusProps) {
  const pct = Math.round((encryptedFields / Math.max(totalFields, 1)) * 100);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Config Encryption</h3>
        <span className="text-xs text-gray-400">{encryptedFields}/{totalFields} encrypted ({pct}%)</span>
      </div>
      {unencryptedSensitive.length > 0 && (
        <div className="p-3 bg-yellow-50 dark:bg-yellow-900/10 border-b dark:border-gray-700">
          <div className="text-xs text-yellow-700 mb-1">⚠ Unencrypted sensitive fields:</div>
          <div className="flex gap-1 flex-wrap">
            {unencryptedSensitive.map(f => (
              <button key={f} onClick={() => onEncrypt(f)}
                className="px-2 py-0.5 text-[10px] bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200">
                🔓 {f}
              </button>
            ))}
          </div>
        </div>
      )}
      <div className="p-3">
        <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className={`h-full rounded-full ${pct === 100 ? "bg-green-500" : "bg-yellow-500"}`}
            style={{ width: `${pct}%` }} />
        </div>
      </div>
    </div>
  );
}
