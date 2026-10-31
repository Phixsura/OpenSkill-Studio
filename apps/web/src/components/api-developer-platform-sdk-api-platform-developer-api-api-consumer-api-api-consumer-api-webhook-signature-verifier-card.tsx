"use client";

interface Props { webhookId: string; algorithm: string; toleranceSec: number; replayWindow: number; recentVerifications: { valid: boolean; reason: string; }[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSignatureVerifierCard({ webhookId, algorithm, toleranceSec, replayWindow, recentVerifications, appName }: Props) {
  const validCount = recentVerifications.filter((v) => v.valid).length;
  const total = recentVerifications.length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Signature Verifier</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {webhookId}</p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
          <div className="font-bold text-gray-700 dark:text-gray-300">{algorithm.toUpperCase()}</div>
          <div className="text-[10px] text-gray-400">Algorithm</div>
        </div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
          <div className="font-bold text-gray-700 dark:text-gray-300">{toleranceSec}s</div>
          <div className="text-[10px] text-gray-400">Tolerance</div>
        </div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
          <div className="font-bold text-gray-700 dark:text-gray-300">{replayWindow}</div>
          <div className="text-[10px] text-gray-400">Replay window</div>
        </div>
      </div>
      {total > 0 ? (
        <div className="text-[11px] text-gray-500">
          Verified: <span className="font-medium text-green-600">{validCount}</span> / {total}
          {total - validCount > 0 && <span className="ml-1 text-red-500">({total - validCount} rejected)</span>}
        </div>
      ) : (
        <p className="text-center text-sm text-gray-400">No verifications yet</p>
      )}
    </div>
  );
}
