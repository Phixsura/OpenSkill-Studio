"use client";

interface Props { consumerId: string; supportedFormats: string[]; defaultFormat: string; strict: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiContentNegotiationCard({ consumerId, supportedFormats, defaultFormat, strict, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Content Negotiation</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="space-y-2 text-[11px]">
        <div className="flex justify-between"><span className="text-gray-500">Default:</span><code className="text-gray-700 dark:text-gray-300">{defaultFormat}</code></div>
        <div className="flex justify-between"><span className="text-gray-500">Mode:</span><span className={strict ? "font-bold text-red-600" : "text-green-600"}>{strict ? "Strict" : "Flexible"}</span></div>
        <div>
          <span className="text-gray-500">Supported:</span>
          <div className="mt-0.5 flex flex-wrap gap-1">
            {supportedFormats.map((f) => (
              <span key={f} className={`rounded px-1.5 py-0.5 text-[10px] ${f === defaultFormat ? "bg-blue-100 font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"}`}>{f.split("/")[1]}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
