"use client";

import { useState } from "react";

import { MediaPreview } from "@/components/media-preview";

export interface VersionItem {
  id: string;
  file_name: string | null;
  mime_type: string | null;
  version: number;
  note?: string | null;
}

interface VersionCompareProps {
  /** All versions of one deliverable, any order. */
  items: VersionItem[];
  /** Builds the presigned-download API path for an item. */
  downloadPath: (itemId: string) => string;
}

/**
 * Side-by-side version comparison (Frame.io Comparison Viewer semantics):
 * pick any two versions of a deliverable and view them next to each other.
 * Defaults to latest vs previous.
 */
export function VersionCompare({ items, downloadPath }: VersionCompareProps) {
  const sorted = [...items].sort((a, b) => b.version - a.version);
  const [open, setOpen] = useState(false);
  const [leftId, setLeftId] = useState<string | null>(null);
  const [rightId, setRightId] = useState<string | null>(null);

  if (sorted.length < 2) return null;

  const left = sorted.find((i) => i.id === leftId) ?? sorted[1]!;
  const right = sorted.find((i) => i.id === rightId) ?? sorted[0]!;

  const Selector = ({
    value,
    onChange,
    exclude,
  }: {
    value: VersionItem;
    onChange: (id: string) => void;
    exclude: string;
  }) => (
    <select
      className="rounded-md border bg-transparent px-2 py-1 text-xs"
      value={value.id}
      onChange={(e) => onChange(e.target.value)}
    >
      {sorted.map((i) => (
        <option key={i.id} value={i.id} disabled={i.id === exclude}>
          v{i.version} — {i.file_name ?? "file"}
        </option>
      ))}
    </select>
  );

  return (
    <div data-testid="version-compare">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="rounded border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
      >
        {open ? "Hide comparison" : `⇄ Compare versions (${sorted.length})`}
      </button>

      {open && (
        <div className="mt-2 grid gap-3 sm:grid-cols-2">
          {[
            { item: left, set: setLeftId, other: right.id },
            { item: right, set: setRightId, other: left.id },
          ].map(({ item, set, other }, idx) => (
            <div key={idx} className="space-y-1.5 rounded-md border p-2">
              <div className="flex items-center justify-between gap-2">
                <Selector value={item} onChange={set} exclude={other} />
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    item.version === sorted[0]!.version
                      ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200"
                      : "bg-[hsl(var(--secondary))] text-[hsl(var(--muted-foreground))]"
                  }`}
                >
                  v{item.version}
                  {item.version === sorted[0]!.version ? " · latest" : ""}
                </span>
              </div>
              <MediaPreview
                downloadPath={downloadPath(item.id)}
                mimeType={item.mime_type}
                fileName={item.file_name}
              />
              {item.note && (
                <p className="text-xs text-[hsl(var(--muted-foreground))]">📝 {item.note}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
