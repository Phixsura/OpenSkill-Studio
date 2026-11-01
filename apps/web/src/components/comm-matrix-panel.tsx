"use client";
interface CommMatrixPanelProps { services: string[]; rows: Record<string, number | string>[]; totalComms: number; }
export function CommMatrixPanel({ services, rows, totalComms }: CommMatrixPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Communication Matrix</h3>
        <span className="text-xs text-gray-400">{services.length} services · {totalComms.toLocaleString()} calls</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-[10px]">
          <thead><tr><th className="px-2 py-1 text-left">→</th>
            {services.map(s => <th key={s} className="px-2 py-1 text-gray-400">{s}</th>)}
          </tr></thead>
          <tbody>{rows.map(row => (
            <tr key={row.service as string} className="border-t dark:border-gray-700">
              <td className="px-2 py-1 font-mono font-bold">{row.service as string}</td>
              {services.map(s => (
                <td key={s} className="px-2 py-1 text-center text-gray-400">
                  {(row[s] as number) > 0 ? (row[s] as number).toLocaleString() : "-"}
                </td>
              ))}
            </tr>
          ))}</tbody>
        </table>
      </div>
    </div>
  );
}
