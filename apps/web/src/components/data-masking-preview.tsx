"use client";

interface MaskedField { key: string; original: string; masked: string; type: string; }
interface DataMaskingPreviewProps { fields: MaskedField[]; fieldsMasked: number; }

const typeIcon: Record<string, string> = {
  email: "📧", phone: "📱", credit_card: "💳", api_key: "🔑", password: "🔒", ssn: "🆔",
};

export function DataMaskingPreview({ fields, fieldsMasked }: DataMaskingPreviewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Data Masking</h2>
        <span className="text-xs text-gray-400">{fieldsMasked} fields masked</span>
      </div>
      <div className="space-y-1.5">
        {fields.map(f => (
          <div key={f.key} className="rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{typeIcon[f.type] ?? "🔒"}</span>
              <span className="text-sm font-medium">{f.key}</span>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] dark:bg-gray-800">{f.type}</span>
            </div>
            <div className="mt-1 grid grid-cols-2 gap-2 font-mono text-xs">
              <div><span className="text-gray-400">Original: </span><span className="text-red-400 line-through">{f.original}</span></div>
              <div><span className="text-gray-400">Masked: </span><span className="text-green-500">{f.masked}</span></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
