"use client";

interface SlotInfo { version: string; healthy: boolean; }
interface BlueGreenStatusProps { active: string; slots: Record<string, SlotInfo>; }

export function BlueGreenStatus({ active, slots }: BlueGreenStatusProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔵🟢 Blue-Green Deploy</h3>
        <span className="text-xs text-gray-400">active: {active}</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4">
        {Object.entries(slots).map(([name, slot]) => (
          <div key={name} className={`rounded-lg p-3 border-2 ${
            name === active ? "border-blue-500 bg-blue-50 dark:bg-blue-950" : "border-gray-300 dark:border-gray-600"}`}>
            <div className="flex items-center justify-between mb-1">
              <span className={`text-xs font-bold uppercase ${name === "blue" ? "text-blue-600" : "text-green-600"}`}>{name}</span>
              {name === active && <span className="text-[10px] bg-blue-500 text-white px-1 rounded">LIVE</span>}
            </div>
            <div className="text-xs text-gray-500">{slot.version || "empty"}</div>
            <div className={`text-xs mt-1 ${slot.healthy ? "text-green-600" : "text-gray-400"}`}>
              {slot.healthy ? "healthy" : "not ready"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
