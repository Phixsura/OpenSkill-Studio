"use client";

interface DnsRecord { domain: string; type: string; value: string; ttl: number; }
interface DnsRecordEditorProps { records: DnsRecord[];
  onAdd: () => void; onDelete: (domain: string, type: string, value: string) => void; }

const TYPE_COLORS: Record<string, string> = {
  A: "bg-blue-100 text-blue-700", AAAA: "bg-indigo-100 text-indigo-700",
  CNAME: "bg-green-100 text-green-700", TXT: "bg-yellow-100 text-yellow-700",
  MX: "bg-purple-100 text-purple-700", NS: "bg-gray-100 text-gray-700",
};

export function DnsRecordEditor({ records, onAdd, onDelete }: DnsRecordEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 DNS Records</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{records.length} records</span>
          <button onClick={onAdd} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Add</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {records.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`px-1.5 py-0.5 text-[10px] rounded font-mono ${TYPE_COLORS[r.type] ?? ""}`}>{r.type}</span>
              <span className="text-sm font-mono">{r.domain}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-gray-400 max-w-[180px] truncate">{r.value}</span>
              <span className="text-[10px] text-gray-300">{r.ttl}s</span>
              <button onClick={() => onDelete(r.domain, r.type, r.value)} className="text-xs text-red-500">×</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
