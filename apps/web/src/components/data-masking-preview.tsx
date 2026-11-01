"use client";

interface MaskedRecord { [key: string]: unknown; }
interface DataMaskingPreviewProps { records: MaskedRecord[]; fieldsMasked: number;
  sensitiveFields: string[]; }

export function DataMaskingPreview({ records, fieldsMasked, sensitiveFields }: DataMaskingPreviewProps) {
  if (records.length === 0) return null;
  const keys = Object.keys(records[0]);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 Data Masking</h3>
        <span className="text-xs text-gray-400">{fieldsMasked} fields masked · {records.length} records</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead><tr className="text-gray-400 border-b dark:border-gray-700">
            {keys.map(k => (
              <th key={k} className="p-2 text-left">
                {k} {sensitiveFields.includes(k) && <span className="text-red-400">🔒</span>}
              </th>
            ))}
          </tr></thead>
          <tbody>
            {records.map((r, i) => (
              <tr key={i} className="border-b last:border-0 dark:border-gray-700">
                {keys.map(k => (
                  <td key={k} className={`p-2 font-mono ${sensitiveFields.includes(k) ? "text-gray-400" : ""}`}>
                    {String(r[k])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
