"use client";

interface EventReplayDialogProps {
  eventCount: number; targetUrl: string;
  onConfirm: () => void; onCancel: () => void; isReplaying?: boolean;
}

export function EventReplayDialog({ eventCount, targetUrl, onConfirm, onCancel, isReplaying }: EventReplayDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" role="dialog" aria-label="Replay events">
      <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <div className="text-center text-3xl">🔄</div>
        <h2 className="mt-2 text-center text-lg font-semibold">Replay Events</h2>
        <p className="mt-2 text-center text-sm text-gray-500">
          Replay {eventCount} event{eventCount !== 1 ? "s" : ""} to:
        </p>
        <p className="mt-1 text-center font-mono text-xs text-blue-600">{targetUrl}</p>
        <div className="mt-4 rounded bg-yellow-50 p-3 text-xs text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300">
          ⚠️ Events will be delivered again. Your endpoint should handle duplicates.
        </div>
        <div className="mt-4 flex justify-center gap-3">
          <button onClick={onCancel} className="rounded px-4 py-2 text-sm text-gray-600">Cancel</button>
          <button onClick={onConfirm} disabled={isReplaying}
            className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50">
            {isReplaying ? "Replaying..." : "Replay"}
          </button>
        </div>
      </div>
    </div>
  );
}
