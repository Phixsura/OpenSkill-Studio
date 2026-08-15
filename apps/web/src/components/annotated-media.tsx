"use client";

import { useEffect, useRef, useState } from "react";

import { apiWithAuth } from "@/lib/api";

export interface CommentRegion {
  type: "rectangle" | "ellipse" | "point";
  bounds: { minX: number; minY: number; maxX: number; maxY: number };
}

export interface ItemComment {
  id: string;
  item_id: string;
  author_id: string;
  parent_id: string | null;
  text: string;
  anchor_type: "global" | "time" | "region";
  timestamp_ms: number | null;
  duration_ms: number | null;
  region: CommentRegion | null;
  completed: boolean;
  created_at: string;
}

interface AnnotatedImageProps {
  downloadPath: string;
  fileName?: string | null;
  comments: ItemComment[];
  /** Index (1-based pin number) of region comments, in comment order. */
  activeCommentId?: string | null;
  onSelectComment?: (id: string | null) => void;
  /** When set, clicking-dragging on the image creates a pending region and
   * calls this with normalized bounds. */
  onDrawRegion?: (region: CommentRegion) => void;
  drawing?: boolean;
}

/**
 * Image with a region-annotation overlay.
 *
 * Coordinates are normalized 0-1 (Annotorious/W3C convention) so pins stay
 * accurate at any rendered size. Pins and the comment list highlight each
 * other bidirectionally (Ziflow UX).
 */
export function AnnotatedImage({
  downloadPath,
  fileName,
  comments,
  activeCommentId,
  onSelectComment,
  onDrawRegion,
  drawing,
}: AnnotatedImageProps) {
  const [url, setUrl] = useState<string | null>(null);
  const [error, setError] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);
  const [dragCurrent, setDragCurrent] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    let cancelled = false;
    apiWithAuth<{ download_url: string }>(downloadPath)
      .then((res) => {
        if (!cancelled) setUrl(res.download_url);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, [downloadPath]);

  const regionComments = comments.filter((c) => c.anchor_type === "region" && c.region);

  const toNormalized = (e: React.MouseEvent): { x: number; y: number } | null => {
    const el = containerRef.current;
    if (!el) return null;
    const rect = el.getBoundingClientRect();
    const x = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
    const y = Math.min(1, Math.max(0, (e.clientY - rect.top) / rect.height));
    return { x, y };
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!drawing || !onDrawRegion) return;
    const p = toNormalized(e);
    if (p) {
      setDragStart(p);
      setDragCurrent(p);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!dragStart) return;
    setDragCurrent(toNormalized(e));
  };

  const handleMouseUp = () => {
    if (dragStart && dragCurrent && onDrawRegion) {
      const minX = Math.min(dragStart.x, dragCurrent.x);
      const minY = Math.min(dragStart.y, dragCurrent.y);
      const maxX = Math.max(dragStart.x, dragCurrent.x);
      const maxY = Math.max(dragStart.y, dragCurrent.y);
      // Tiny drag = point annotation
      if (maxX - minX < 0.01 && maxY - minY < 0.01) {
        onDrawRegion({ type: "point", bounds: { minX, minY, maxX: minX, maxY: minY } });
      } else {
        onDrawRegion({ type: "rectangle", bounds: { minX, minY, maxX, maxY } });
      }
    }
    setDragStart(null);
    setDragCurrent(null);
  };

  if (error) {
    return (
      <div className="rounded-md border border-dashed p-3 text-sm text-[hsl(var(--muted-foreground))]">
        Preview unavailable{fileName ? ` — ${fileName}` : ""}
      </div>
    );
  }

  if (!url) {
    return (
      <div className="flex h-40 animate-pulse items-center justify-center rounded-md bg-[hsl(var(--secondary))]">
        <span className="text-xs text-[hsl(var(--muted-foreground))]">Loading…</span>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      data-testid="annotated-image"
      className={`relative inline-block max-w-full select-none ${drawing ? "cursor-crosshair" : ""}`}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={url}
        alt={fileName ?? "submission"}
        className="max-h-[32rem] w-auto rounded-md border"
        draggable={false}
      />

      {/* Existing region annotations */}
      {regionComments.map((c, i) => {
        const b = c.region!.bounds;
        const isPoint = c.region!.type === "point";
        const active = c.id === activeCommentId;
        const style: React.CSSProperties = isPoint
          ? { left: `${b.minX * 100}%`, top: `${b.minY * 100}%` }
          : {
              left: `${b.minX * 100}%`,
              top: `${b.minY * 100}%`,
              width: `${(b.maxX - b.minX) * 100}%`,
              height: `${(b.maxY - b.minY) * 100}%`,
            };
        return (
          <button
            key={c.id}
            type="button"
            data-testid={`annotation-${i + 1}`}
            onClick={(e) => {
              e.stopPropagation();
              onSelectComment?.(active ? null : c.id);
            }}
            className={`absolute ${
              isPoint ? "-translate-x-1/2 -translate-y-1/2" : ""
            } ${
              active
                ? "border-2 border-blue-500 bg-blue-500/20"
                : "border-2 border-amber-500 bg-amber-500/10 hover:bg-amber-500/20"
            } ${isPoint ? "h-4 w-4 rounded-full border-2" : "rounded-sm"}`}
            style={style}
            title={c.text}
          >
            <span
              className={`absolute -left-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold text-white ${
                active ? "bg-blue-500" : "bg-amber-500"
              } ${c.completed ? "opacity-50" : ""}`}
            >
              {i + 1}
            </span>
          </button>
        );
      })}

      {/* Live drag rectangle */}
      {dragStart && dragCurrent && (
        <div
          className="pointer-events-none absolute rounded-sm border-2 border-dashed border-blue-500 bg-blue-500/10"
          style={{
            left: `${Math.min(dragStart.x, dragCurrent.x) * 100}%`,
            top: `${Math.min(dragStart.y, dragCurrent.y) * 100}%`,
            width: `${Math.abs(dragCurrent.x - dragStart.x) * 100}%`,
            height: `${Math.abs(dragCurrent.y - dragStart.y) * 100}%`,
          }}
        />
      )}
    </div>
  );
}
