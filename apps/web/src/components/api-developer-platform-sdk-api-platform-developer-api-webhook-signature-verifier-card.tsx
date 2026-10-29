"use client";

interface VerifierInfo { consumer_id: string; algorithm: string; valid_count: number; invalid_count: number; }
interface Props { verifiers: VerifierInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookSignatureVerifierCard({ verifiers, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✍️ Signature Verifier</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {verifiers.length} consumers</p>
      </div>
      {verifiers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No verifiers configured</p>
      ) : (
        <div className="space-y-1.5">
          {verifiers.map((v) => (
            <div key={v.consumer_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="text-gray-700 dark:text-gray-300">{v.consumer_id}</span>
                <span className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{v.algorithm}</span>
              </div>
              <span className="text-gray-400">✅{v.valid_count} ❌{v.invalid_count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
