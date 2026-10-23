"use client";

interface IdempotencyKeyViewerProps { total: number; active: number; withResponse: number;
  onCleanup: () => void; }

export function IdempotencyKeyViewer({ total, active, withResponse, onCleanup }: IdempotencyKeyViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 Idempotency Keys</h3>
        <button onClick={onCleanup} className="text-xs text-red-500 hover:underline">Cleanup Expired</button>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Total", v: total }, { l: "Active", v: active }, { l: "With Response", v: withResponse }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-4 text-center">
            <div className="text-xl font-bold">{s.v.toLocaleString()}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
