"use client";
interface MeshReplayPanelProps { captured: number; replayed: number; }
export function MeshReplayPanel({ captured, replayed }: MeshReplayPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏮️ Mesh Traffic Replay</h3>
        <span className="text-xs text-gray-400">{captured} captured · {replayed} replayed</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Captured</span><div className="font-bold text-blue-500 text-lg">{captured.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Replayed</span><div className="font-bold text-green-600 text-lg">{replayed.toLocaleString()}</div></div>
      </div>
    </div>
  );
}
