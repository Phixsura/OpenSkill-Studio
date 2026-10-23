"use client";

interface IpEntry { address: string; valid: boolean; isPrivate?: boolean; }
interface IpAllowlistEditorProps { entries: IpEntry[]; validCount: number;
  invalidCount: number; onAdd: (ip: string) => void; onRemove: (ip: string) => void; }

export function IpAllowlistEditor({ entries, validCount, invalidCount, onAdd, onRemove }: IpAllowlistEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🛡️ IP Allowlist</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{validCount} valid</span>
          {invalidCount > 0 && <span className="text-red-500">{invalidCount} invalid</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map(e => (
          <div key={e.address} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${e.valid ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-mono">{e.address}</span>
              {e.isPrivate && <span className="text-[10px] text-gray-400">private</span>}
            </div>
            <button onClick={() => onRemove(e.address)} className="text-xs text-red-500 hover:underline">Remove</button>
          </div>
        ))}
      </div>
      <div className="p-3 border-t dark:border-gray-700">
        <button onClick={() => onAdd("")}
          className="w-full py-1.5 text-xs text-blue-500 border border-dashed border-blue-300 rounded-lg">+ Add IP/CIDR</button>
      </div>
    </div>
  );
}
