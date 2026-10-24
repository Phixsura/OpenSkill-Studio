"use client";

interface WarRoomUpdate { author: string; message: string; seq: number; }
interface WarRoomPanelProps { incidentId: string; title: string; severity: string;
  commander: string; status: string; participants: string[];
  updates: WarRoomUpdate[]; onAddUpdate: (msg: string) => void; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500 text-white", high: "bg-orange-500 text-white",
  medium: "bg-yellow-400", low: "bg-blue-400 text-white",
};

export function WarRoomPanel({ incidentId, title, severity, commander, status, participants, updates, onAddUpdate }: WarRoomPanelProps) {
  return (
    <div className="rounded-xl border-2 border-red-500 dark:border-red-800 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-900/10">
        <div>
          <h3 className="font-semibold text-sm">🚨 War Room: {title}</h3>
          <div className="text-[10px] text-gray-500">{incidentId} · Commander: {commander} · {participants.length} participants</div>
        </div>
        <span className={`px-2 py-0.5 text-xs rounded ${SEV_COLORS[severity] ?? ""}`}>{severity}</span>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-40 overflow-y-auto bg-gray-950 text-gray-200 font-mono text-xs">
        {updates.map(u => (
          <div key={u.seq} className="px-4 py-1.5">
            <span className="text-blue-400">{u.author}</span>: {u.message}
          </div>
        ))}
      </div>
      <div className="p-2 border-t dark:border-gray-700">
        <button onClick={() => onAddUpdate("")} className="w-full py-1.5 text-xs bg-red-500 text-white rounded">+ Add Update</button>
      </div>
    </div>
  );
}
