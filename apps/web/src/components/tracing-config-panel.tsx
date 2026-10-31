"use client";

interface TracingConfigPanelProps { serviceName: string; exporter: string;
  sampler: string; sampleRate: number; dailySpans: number; storageGbDay: number;
  exporters: string[]; onChange: (field: string, value: unknown) => void; }

export function TracingConfigPanel({ serviceName, exporter, sampler, sampleRate, dailySpans, storageGbDay, exporters, onChange }: TracingConfigPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Tracing: {serviceName}</h3>
        <span className="text-xs text-gray-400">{exporter} · {sampler} @ {sampleRate * 100}%</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-sm font-bold">{(dailySpans / 1_000_000).toFixed(1)}M</div>
          <div className="text-[10px] text-gray-400">Daily Spans</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-sm font-bold">{storageGbDay} GB</div>
          <div className="text-[10px] text-gray-400">Storage/Day</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-sm font-bold">{sampleRate * 100}%</div>
          <div className="text-[10px] text-gray-400">Sample Rate</div>
        </div>
      </div>
      <div className="p-3 flex gap-2 flex-wrap">
        {exporters.map(e => (
          <button key={e} onClick={() => onChange("exporter", e)}
            className={`px-2 py-0.5 text-xs rounded ${e === exporter ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{e}</button>
        ))}
      </div>
    </div>
  );
}
