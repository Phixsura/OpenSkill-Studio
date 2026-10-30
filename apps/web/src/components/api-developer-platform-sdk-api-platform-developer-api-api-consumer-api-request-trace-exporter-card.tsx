"use client";

interface ExportInfo { export_id: string; format: string; span_count: number; }
interface Props { exports: ExportInfo[]; totalSpans: number; errorSpanCount: number; traceCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestTraceExporterCard({ exports: exps, totalSpans, errorSpanCount, traceCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Trace Exporter</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {errorSpanCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">❌ {errorSpanCount} errors</span>}
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalSpans.toLocaleString()}</div><div className="text-gray-400">Spans</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{traceCount}</div><div className="text-gray-400">Traces</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{exps.length}</div><div className="text-gray-400">Exports</div></div>
      </div>
    </div>
  );
}
