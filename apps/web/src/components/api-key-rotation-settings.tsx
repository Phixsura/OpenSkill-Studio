"use client";

interface ApiKeyRotationSettingsProps { maxAgeDays: number; overlapHours: number;
  autoRotate: boolean; nextRotationDays: number; policySummary: string;
  onRotateNow: () => void; onToggleAuto: () => void; }

export function ApiKeyRotationSettings({ maxAgeDays, overlapHours, autoRotate,
  nextRotationDays, policySummary, onRotateNow, onToggleAuto }: ApiKeyRotationSettingsProps) {
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <h2 className="text-lg font-semibold">Key Rotation Policy</h2>
      <p className="text-sm text-gray-400">{policySummary}</p>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{maxAgeDays}d</p>
          <p className="text-xs text-gray-400">Max Age</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{overlapHours}h</p>
          <p className="text-xs text-gray-400">Overlap</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{nextRotationDays}d</p>
          <p className="text-xs text-gray-400">Next Rotation</p>
        </div>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm">Auto-rotate</span>
          <button onClick={onToggleAuto}
            className={`relative h-6 w-11 rounded-full ${autoRotate ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"}`}>
            <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow ${autoRotate ? "left-[1.375rem]" : "left-0.5"}`} />
          </button>
        </div>
        <button onClick={onRotateNow} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">
          Rotate Now
        </button>
      </div>
    </div>
  );
}
