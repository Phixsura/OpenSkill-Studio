"use client";

interface PinnedEntryInfo {
  entry_id: string;
  version: string;
  title: string;
  reason: string;
  pinned_by: string;
}

interface ChangelogPinCardProps {
  pins: PinnedEntryInfo[];
  maxPins: number;
  appName: string;
}

export default function ChangelogPinCard({ pins, maxPins, appName }: ChangelogPinCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📌 Pinned Changes
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {pins.length}/{maxPins} pinned
        </span>
      </div>

      {pins.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No pinned entries</p>
      ) : (
        <div className="space-y-2">
          {pins.map((p) => (
            <div
              key={p.entry_id}
              className="rounded-lg border border-yellow-200 bg-yellow-50/50 px-3 py-2 dark:border-yellow-900/50 dark:bg-yellow-950/10"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {p.title}
                </span>
                <span className="font-mono text-[10px] text-gray-400">v{p.version}</span>
              </div>
              {p.reason && <p className="mt-0.5 text-[11px] text-gray-500">{p.reason}</p>}
              {p.pinned_by && (
                <p className="mt-0.5 text-[10px] text-gray-400">pinned by {p.pinned_by}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
