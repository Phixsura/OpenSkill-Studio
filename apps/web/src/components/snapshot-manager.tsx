"use client";

interface Snapshot { snapshot_id: string; name: string; created_at: string; filesystem_files: number; }
interface SnapshotManagerProps { snapshots: Snapshot[]; onRestore: (id: string) => void; onDelete: (id: string) => void; }

export function SnapshotManager({ snapshots, onRestore, onDelete }: SnapshotManagerProps) {
  if (snapshots.length === 0) return <p className="text-sm text-gray-400">No snapshots saved.</p>;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Snapshots</h3>
      <ul className="mt-3 space-y-2">
        {snapshots.map(s => (
          <li key={s.snapshot_id} className="flex items-center justify-between rounded border p-2 dark:border-gray-700">
            <div>
              <p className="text-sm font-medium">{s.name}</p>
              <p className="text-xs text-gray-400">{s.created_at.slice(0, 10)} · {s.filesystem_files} files</p>
            </div>
            <div className="flex gap-1">
              <button onClick={() => onRestore(s.snapshot_id)} className="rounded bg-blue-100 px-2 py-1 text-xs text-blue-700">Restore</button>
              <button onClick={() => onDelete(s.snapshot_id)} className="rounded bg-red-100 px-2 py-1 text-xs text-red-700">Delete</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
