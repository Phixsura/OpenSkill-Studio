"use client";
interface MockDataPanelProps { dataType: string; count: number; fields: string[]; sampleId: string; }
export function MockDataPanel({ dataType, count, fields, sampleId }: MockDataPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎲 Mock Data: {dataType}</h3>
        <span className="text-xs text-gray-400">{count} records · {fields.length} fields</span>
      </div>
      <div className="p-4 text-xs">
        <div className="text-gray-400 mb-1">Fields: {fields.join(", ")}</div>
        <div className="text-gray-400">Sample: {sampleId}</div>
      </div>
    </div>
  );
}
