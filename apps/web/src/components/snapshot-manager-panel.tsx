"use client";

import { useState } from "react";

interface Snapshot {
  snapshotId: string;
  label: string;
  sizeBytes: number;
  fileCount: number;
  createdAt: string;
  createdBy: string;
}

interface SnapshotDiff {
  added: string[];
  removed: string[];
  modified: string[];
  hasChanges: boolean;
}

function formatSize(b: number) {
  if (b < 1024) return `${b}B`;
  if (b < 1048576) return `${(b / 1024).toFixed(1)}KB`;
  return `${(b / 1048576).toFixed(1)}MB`;
}

export function SnapshotManagerPanel({
  snapshots,
  diff,
  onCapture,
  onRestore,
  onDelete,
  onCompare,
}: {
  snapshots: Snapshot[];
  diff: SnapshotDiff | null;
  onCapture?: (label: string) => void;
  onRestore?: (id: string) => void;
  onDelete?: (id: string) => void;
  onCompare?: (id1: string, id2: string) => void;
}) {
  const [label, setLabel] = useState("");
  const [showDiff, setShowDiff] = useState(false);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📸 Snapshots</h2>
        <span className="text-sm text-gray-500">{snapshots.length} saved</span>
      </div>

      <div className="flex gap-2">
        <input type="text" value={label} onChange={(e) => setLabel(e.target.value)}
          placeholder="Snapshot label..."
          className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm" />
        <button onClick={() => { onCapture?.(label); setLabel(""); }}
          disabled={!label.trim()}
          className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg disabled:opacity-50">Capture</button>
      </div>

      <div className="space-y-1">
        {snapshots.map((snap, i) => (
          <div key={snap.snapshotId} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
            <div>
              <span className="font-semibold text-sm">{snap.label}</span>
              <div className="text-xs text-gray-500 mt-0.5">
                {snap.fileCount} files · {formatSize(snap.sizeBytes)} · {snap.createdAt}
              </div>
            </div>
            <div className="flex gap-1">
              {i > 0 && (
                <button onClick={() => { onCompare?.(snapshots[i - 1].snapshotId, snap.snapshotId); setShowDiff(true); }}
                  className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Diff</button>
              )}
              <button onClick={() => onRestore?.(snap.snapshotId)}
                className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Restore</button>
              <button onClick={() => onDelete?.(snap.snapshotId)}
                className="text-xs text-red-500">✕</button>
            </div>
          </div>
        ))}
      </div>

      {showDiff && diff && (
        <div className="rounded-lg border dark:border-gray-700 p-3 space-y-1">
          <span className="text-sm font-semibold">Changes</span>
          {diff.added.map((f) => <div key={f} className="text-xs text-green-600">+ {f}</div>)}
          {diff.removed.map((f) => <div key={f} className="text-xs text-red-600">- {f}</div>)}
          {diff.modified.map((f) => <div key={f} className="text-xs text-yellow-600">~ {f}</div>)}
          {!diff.hasChanges && <span className="text-xs text-gray-500">No changes</span>}
        </div>
      )}
    </div>
  );
}
