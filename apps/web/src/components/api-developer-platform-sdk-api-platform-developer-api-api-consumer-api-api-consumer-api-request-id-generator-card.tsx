"use client";

interface Props { totalGenerated: number; format: string; prefix: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIdGeneratorCard({ totalGenerated, format, prefix, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🆔 Request ID Generator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalGenerated.toLocaleString()} generated</span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{prefix}-*</div><div className="text-gray-400">Prefix</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{format}</div><div className="text-gray-400">Format</div></div>
      </div>
    </div>
  );
}
