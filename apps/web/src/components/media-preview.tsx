"use client";

import { useEffect, useState } from "react";

import { Lightbox } from "@/components/lightbox";
import { apiWithAuth } from "@/lib/api";

interface MediaPreviewProps {
  /** API path that returns { download_url } (relative to /api/v1) */
  downloadPath: string;
  mimeType: string | null;
  fileName?: string | null;
  className?: string;
}

/**
 * Fetches a presigned URL for a media file and renders the appropriate
 * preview element: <img> for images, <video> for video, <audio> for audio,
 * and a download link for everything else. Falls back to a download link
 * on any error.
 */
export function MediaPreview({ downloadPath, mimeType, fileName, className }: MediaPreviewProps) {
  const [url, setUrl] = useState<string | null>(null);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  const family = mimeType?.split("/")[0] ?? "";

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    apiWithAuth<{ download_url: string }>(downloadPath)
      .then((res) => {
        if (!cancelled) setUrl(res.download_url);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [downloadPath]);

  if (loading) {
    return (
      <div
        className={`flex h-32 animate-pulse items-center justify-center rounded-md bg-[hsl(var(--secondary))] ${className ?? ""}`}
      >
        <span className="text-xs text-[hsl(var(--muted-foreground))]">Loading preview…</span>
      </div>
    );
  }

  if (error || !url) {
    return (
      <div className={`rounded-md border border-dashed p-3 text-sm ${className ?? ""}`}>
        <span className="text-[hsl(var(--muted-foreground))]">
          Preview unavailable{fileName ? ` — ${fileName}` : ""}
        </span>
      </div>
    );
  }

  if (family === "image") {
    return (
      <>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={url}
          alt={fileName ?? "preview"}
          loading="lazy"
          onClick={() => setExpanded(true)}
          className={`max-h-80 w-auto cursor-zoom-in rounded-md border object-contain ${className ?? ""}`}
        />
        {expanded && (
          <Lightbox url={url} alt={fileName ?? "preview"} onClose={() => setExpanded(false)} />
        )}
      </>
    );
  }

  if (family === "video") {
    return (
      <video
        src={url}
        controls
        preload="metadata"
        className={`max-h-80 w-full rounded-md border ${className ?? ""}`}
      />
    );
  }

  if (family === "audio") {
    return <audio src={url} controls preload="metadata" className={`w-full ${className ?? ""}`} />;
  }

  // PDF and anything else: download link
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-block text-sm text-[hsl(var(--primary))] hover:underline ${className ?? ""}`}
    >
      📄 {fileName ?? "Download file"}
    </a>
  );
}
