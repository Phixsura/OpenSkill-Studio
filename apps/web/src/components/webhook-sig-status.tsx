"use client";

interface WebhookSigStatusProps { verified: number; failed: number; total: number; algorithm: string; }

export function WebhookSigStatus({ verified, failed, total, algorithm }: WebhookSigStatusProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">✍️ Webhook Signatures</h3>
        <span className="text-xs text-gray-400">{algorithm} · {total} checked</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Verified</div><div className="font-bold text-green-600 text-lg">{verified}</div></div>
        <div><div className="text-gray-400">Failed</div><div className={`font-bold text-lg ${failed > 0 ? "text-red-500" : "text-gray-400"}`}>{failed}</div></div>
      </div>
    </div>
  );
}
