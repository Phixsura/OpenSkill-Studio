"use client";

interface SavingsInfo { total_original_kb: number; total_compressed_kb: number; saved_kb: number; savings_pct: number; count: number; }
interface Props { savings: SavingsInfo; algorithm: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadCompressorCard({ savings, algorithm, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗜️ Payload Compressor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {algorithm}</p>
        </div>
        <span className="text-sm font-bold text-green-600 dark:text-green-400">{savings.savings_pct}% saved</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{savings.total_original_kb} KB</div><div className="text-gray-400">Original</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{savings.total_compressed_kb} KB</div><div className="text-gray-400">Compressed</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{savings.count.toLocaleString()}</div><div className="text-gray-400">Payloads</div></div>
      </div>
    </div>
  );
}
