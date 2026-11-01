"use client";

interface IdempotencyKeyInfoProps { apiKey: string; expiresAt: string;
  onGenerate: () => void; onCopy: (key: string) => void; }

export function IdempotencyKeyInfo({ apiKey, expiresAt, onGenerate, onCopy }: IdempotencyKeyInfoProps) {
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <h3 className="text-sm font-semibold">Idempotency Key</h3>
      <p className="mt-1 text-xs text-gray-400">
        Include this header to prevent duplicate operations:
      </p>
      <div className="mt-2 flex items-center gap-2 rounded bg-gray-900 px-3 py-2 font-mono text-xs text-green-400">
        <span className="flex-1 truncate">Idempotency-Key: {apiKey}</span>
        <button onClick={() => onCopy(apiKey)} className="flex-shrink-0 text-blue-400">Copy</button>
      </div>
      <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
        <span>Expires: {new Date(expiresAt).toLocaleString()}</span>
        <button onClick={onGenerate} className="text-blue-500">Generate New</button>
      </div>
    </div>
  );
}
