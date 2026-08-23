"use client";

import { useState } from "react";
import { toast } from "sonner";

import { apiWithAuth } from "@/lib/api";

interface VersionItem {
  id: string;
  version: number;
  file_name: string | null;
  mime_type: string | null;
  note: string | null;
  created_at: string;
}

/**
 * Expandable version history for a deliverable's uploads (issue #9 §7:
 * previous versions must remain accessible). Shows every version with
 * thumbnail, note, timestamp, and download.
 */
export function VersionHistory({
  items,
  downloadPath,
}: {
  items: VersionItem[];
  downloadPath: (itemId: string) => string;
}) {
  const [open, setOpen] = useState(false);
  const [thumbs, setThumbs] = useState<Record<string, string>>({});

  if (items.length < 2) return null;
  const sorted = [...items].sort((a, b) => b.version - a.version);

  const loadThumb = async (itemId: string) => {
    if (thumbs[itemId]) return;
    try {
      const res = await apiWithAuth<{ download_url: string }>(downloadPath(itemId));
      setThumbs((t) => ({ ...t, [itemId]: res.download_url }));
    } catch {
      // ignore — leave placeholder
    }
  };

  const toggle = () => {
    const next = !open;
    setOpen(next);
    if (next) {
      for (const it of sorted) {
        if (it.mime_type?.startsWith("image/")) void loadThumb(it.id);
      }
    }
  };

  return (
    <div data-testid="version-history">
      <button
        type="button"
        onClick={toggle}
        className="rounded border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
      >
        🕘 Version history ({items.length})
      </button>

      {open && (
        <ol className="mt-2 space-y-2 border-l-2 pl-3">
          {sorted.map((it, idx) => (
            <li key={it.id} className="flex items-start gap-3 text-sm">
              {it.mime_type?.startsWith("image/") ? (
                thumbs[it.id] ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={thumbs[it.id]}
                    alt={`v${it.version}`}
                    className="h-12 w-12 rounded border object-cover"
                  />
                ) : (
                  <span className="flex h-12 w-12 items-center justify-center rounded border text-xs text-[hsl(var(--muted-foreground))]">
                    …
                  </span>
                )
              ) : (
                <span className="flex h-12 w-12 items-center justify-center rounded border text-lg">
                  📄
                </span>
              )}
              <div className="min-w-0 flex-1">
                <p className="flex items-center gap-2">
                  <span className="font-medium">v{it.version}</span>
                  {idx === 0 && (
                    <span className="rounded-full bg-green-100 px-1.5 py-0.5 text-[10px] font-medium text-green-700 dark:bg-green-900 dark:text-green-200">
                      latest
                    </span>
                  )}
                  <span className="truncate text-xs text-[hsl(var(--muted-foreground))]">
                    {it.file_name}
                  </span>
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">
                  {new Date(it.created_at).toLocaleString()}
                  {it.note && <span className="ml-2 italic">“{it.note}”</span>}
                </p>
              </div>
              <button
                type="button"
                className="shrink-0 rounded border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
                onClick={async () => {
                  try {
                    const res = await apiWithAuth<{ download_url: string }>(
                      downloadPath(it.id),
                    );
                    window.open(res.download_url, "_blank", "noopener");
                  } catch {
                    toast.error("Download failed. Please try again.");
                  }
                }}
              >
                Download
              </button>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
