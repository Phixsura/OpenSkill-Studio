"use client";

interface KeyRotationStatusProps { newPrefix: string; oldPrefix: string;
  graceUntil: string; status: string; oldKeyActive: boolean;
  onRotate: () => void; }

export function KeyRotationStatus({ newPrefix, oldPrefix, graceUntil, status,
  oldKeyActive, onRotate }: KeyRotationStatusProps) {
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">🔑 Key Rotation</h3>
        <span className={`rounded px-2 py-0.5 text-xs ${status === "completed" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30"}`}>
          {status === "completed" ? "✓ Completed" : "⏳ Grace period"}
        </span>
      </div>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-400">New key</span>
          <code className="font-mono">{newPrefix}••••</code>
        </div>
        {oldKeyActive && (
          <div className="flex justify-between">
            <span className="text-gray-400">Old key (active until)</span>
            <span className="text-xs">{new Date(graceUntil).toLocaleDateString()}</span>
          </div>
        )}
      </div>
      <button onClick={onRotate} className="mt-3 w-full rounded border py-1.5 text-xs dark:border-gray-700">Rotate Again</button>
    </div>
  );
}
