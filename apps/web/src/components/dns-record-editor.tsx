"use client";

interface DnsRecord { type: string; name: string; value: string; ttl: number; }
interface DnsRecordEditorProps { domain: string; records: DnsRecord[];
  onAdd: (type: string, name: string, value: string) => void;
  onRemove: (name: string, type: string) => void; }

const TYPE_COLOR: Record<string, string> = {
  A: "bg-green-100 text-green-700", AAAA: "bg-green-100 text-green-700",
  CNAME: "bg-blue-100 text-blue-700", TXT: "bg-purple-100 text-purple-700",
  MX: "bg-yellow-100 text-yellow-700", NS: "bg-gray-100 text-gray-700",
};

export function DnsRecordEditor({ domain, records, onAdd, onRemove }: DnsRecordEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 DNS Records</h3>
        <p className="text-xs text-gray-400">{domain} · {records.length} records</p>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Type</th><th className="p-3 text-left">Name</th>
          <th className="p-3 text-left">Value</th><th className="p-3">TTL</th><th className="p-3"></th>
        </tr></thead>
        <tbody>
          {records.map((r, i) => (
            <tr key={i} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3"><span className={`text-xs px-1.5 py-0.5 rounded font-bold ${TYPE_COLOR[r.type] || ""}`}>{r.type}</span></td>
              <td className="p-3 font-mono text-xs">{r.name}</td>
              <td className="p-3 font-mono text-xs truncate max-w-xs">{r.value}</td>
              <td className="p-3 text-center text-xs text-gray-400">{r.ttl}</td>
              <td className="p-3 text-right">
                <button onClick={() => onRemove(r.name, r.type)} className="text-xs text-red-500 hover:text-red-700">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
