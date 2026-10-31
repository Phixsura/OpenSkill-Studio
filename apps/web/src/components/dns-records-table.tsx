"use client";

interface DnsRecord { type: string; name: string; value: string; ttl: number; }
interface DnsRecordsTableProps { records: DnsRecord[]; onDelete: (idx: number) => void; }

const typeColors: Record<string, string> = {
  A: "bg-blue-100 text-blue-700", AAAA: "bg-purple-100 text-purple-700",
  CNAME: "bg-green-100 text-green-700", MX: "bg-orange-100 text-orange-700",
  TXT: "bg-yellow-100 text-yellow-700", NS: "bg-gray-100 text-gray-700",
};

export function DnsRecordsTable({ records, onDelete }: DnsRecordsTableProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">DNS Records ({records.length})</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b dark:border-gray-700 text-xs text-gray-400">
            <th className="px-3 py-2 text-left">Type</th><th className="px-3 py-2 text-left">Name</th>
            <th className="px-3 py-2 text-left">Value</th><th className="px-3 py-2 text-right">TTL</th>
            <th className="px-3 py-2"></th>
          </tr></thead>
          <tbody>
            {records.map((r, i) => (
              <tr key={i} className="border-b dark:border-gray-800">
                <td className="px-3 py-2"><span className={`rounded px-1.5 py-0.5 text-xs ${typeColors[r.type] ?? "bg-gray-100"} dark:bg-opacity-30`}>{r.type}</span></td>
                <td className="px-3 py-2 font-mono text-xs">{r.name}</td>
                <td className="px-3 py-2 font-mono text-xs truncate max-w-[200px]">{r.value}</td>
                <td className="px-3 py-2 text-right text-xs text-gray-400">{r.ttl}s</td>
                <td className="px-3 py-2"><button onClick={() => onDelete(i)} className="text-xs text-red-600">×</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
