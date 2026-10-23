"use client";

interface DnsRecord { type: string; name: string; value: string; ttl: number; }
interface DnsRecordTableProps { domain: string; records: DnsRecord[];
  onDelete: (name: string, type: string) => void; onAdd: () => void; }

const typeBadge: Record<string, string> = {
  A: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", AAAA: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
  CNAME: "bg-green-100 text-green-700 dark:bg-green-900/30", TXT: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  MX: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
};

export function DnsRecordTable({ domain, records, onDelete, onAdd }: DnsRecordTableProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">DNS Records</h2>
          <p className="text-xs text-gray-400">{domain}</p>
        </div>
        <button onClick={onAdd} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Add Record</button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-xs text-gray-400 dark:border-gray-700">
              <th className="pb-2">Type</th><th className="pb-2">Name</th>
              <th className="pb-2">Value</th><th className="pb-2">TTL</th><th className="pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {records.map((r, i) => (
              <tr key={i} className="border-b dark:border-gray-800">
                <td className="py-2"><span className={`rounded px-1.5 py-0.5 text-xs font-bold ${typeBadge[r.type] ?? ""}`}>{r.type}</span></td>
                <td className="py-2 font-mono text-xs">{r.name}</td>
                <td className="max-w-[200px] truncate py-2 font-mono text-xs text-gray-400">{r.value}</td>
                <td className="py-2 text-xs text-gray-400">{r.ttl}s</td>
                <td className="py-2"><button onClick={() => onDelete(r.name, r.type)} className="text-xs text-red-500">Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
