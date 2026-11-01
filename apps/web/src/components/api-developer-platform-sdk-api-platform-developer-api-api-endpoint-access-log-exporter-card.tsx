"use client";

interface StatusRanges { "2xx": number; "3xx": number; "4xx": number; "5xx": number; }
interface Props { entryCount: number; statusRanges: StatusRanges; formats: string[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAccessLogExporterCard({ entryCount, statusRanges, formats, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📤 Log Exporter</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {entryCount.toLocaleString()} entries</p>
        </div>
        <div className="flex gap-1">{formats.map((f) => <span key={f} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{f}</span>)}</div>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-green-600">{statusRanges["2xx"]}</div><div className="text-gray-400">2xx</div></div>
        <div><div className="font-semibold text-blue-600">{statusRanges["3xx"]}</div><div className="text-gray-400">3xx</div></div>
        <div><div className="font-semibold text-yellow-600">{statusRanges["4xx"]}</div><div className="text-gray-400">4xx</div></div>
        <div><div className="font-semibold text-red-600">{statusRanges["5xx"]}</div><div className="text-gray-400">5xx</div></div>
      </div>
    </div>
  );
}
