"use client";

interface InspectionInfo { inspection_id: string; event_type: string; payload_size_bytes: number; field_count: number; has_nested: boolean; validation_errors: string[]; }
interface Props { inspections: InspectionInfo[]; errorCount: number; appName: string; }

function fmtSize(b: number) { return b < 1024 ? `${b}B` : `${(b / 1024).toFixed(1)}KB`; }

export default function APIDeveloperAPIWebhookPayloadInspectorCard({ inspections, errorCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Payload Inspector</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {errorCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{errorCount} issues</span>}
      </div>
      {inspections.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No inspections</p>
      ) : (
        <div className="space-y-1.5">
          {inspections.map((i) => (
            <div key={i.inspection_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${i.validation_errors.length > 0 ? "bg-red-500" : "bg-green-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{i.event_type}</span>
              </div>
              <span className="text-gray-400">{fmtSize(i.payload_size_bytes)} · {i.field_count} fields</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
