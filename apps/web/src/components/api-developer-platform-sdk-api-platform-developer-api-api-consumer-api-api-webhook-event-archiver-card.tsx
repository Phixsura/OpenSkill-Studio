"use client";

interface Props { totalArchived: number; totalSizeKb: number; retentionDays: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventArchiverCard({ totalArchived, totalSizeKb, retentionDays, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗄️ Event Archiver</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {retentionDays}d retention</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalArchived.toLocaleString()}</div><div className="text-gray-400">Archived</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalSizeKb.toLocaleString()} KB</div><div className="text-gray-400">Size</div></div>
      </div>
    </div>
  );
}
