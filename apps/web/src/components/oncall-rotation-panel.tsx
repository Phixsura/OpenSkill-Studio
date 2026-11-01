"use client";

interface OnCallInfo { team: string; primary: string; secondary: string; rotationDay: number; }
interface OnCallRotationPanelProps { rotations: OnCallInfo[]; }

export function OnCallRotationPanel({ rotations }: OnCallRotationPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📟 On-Call Rotation</h3>
        <span className="text-xs text-gray-400">{rotations.length} teams</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rotations.map(r => (
          <div key={r.team} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-bold">{r.team}</span>
              <span className="text-gray-400">day {r.rotationDay}</span>
            </div>
            <div className="text-gray-400">
              🟢 <span className="text-blue-500">{r.primary}</span> · 🟡 {r.secondary}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
