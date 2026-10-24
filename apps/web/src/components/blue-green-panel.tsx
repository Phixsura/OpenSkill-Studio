"use client";

interface SlotInfo { version: string; status: string; health: string; }
interface BlueGreenPanelProps { active: string; slots: Record<string, SlotInfo>;
  onSwitch: () => void; onRollback: () => void; }

export function BlueGreenPanel({ active, slots, onSwitch, onRollback }: BlueGreenPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-4">🔄 Blue-Green Deploy</h3>
      <div className="grid grid-cols-2 gap-4 mb-4">
        {(["blue", "green"] as const).map(slot => {
          const s = slots[slot] || { version: "", status: "idle", health: "unknown" };
          const isActive = slot === active;
          return (
            <div key={slot} className={`rounded-lg p-4 text-center border-2 ${
              isActive ? "border-green-500 bg-green-50 dark:bg-green-900/10" : "border-gray-200 dark:border-gray-700"
            }`}>
              <p className={`text-sm font-bold capitalize ${slot === "blue" ? "text-blue-600" : "text-green-600"}`}>{slot}</p>
              <p className="text-lg font-mono font-bold mt-1">{s.version || "—"}</p>
              <p className="text-xs text-gray-400 mt-1">{s.status}</p>
              {isActive && <span className="text-xs text-green-600 font-medium">● Active</span>}
            </div>
          );
        })}
      </div>
      <div className="flex gap-2">
        <button onClick={onSwitch} className="flex-1 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Switch</button>
        <button onClick={onRollback} className="flex-1 py-2 border border-yellow-300 text-yellow-700 text-sm rounded hover:bg-yellow-50">Rollback</button>
      </div>
    </div>
  );
}
