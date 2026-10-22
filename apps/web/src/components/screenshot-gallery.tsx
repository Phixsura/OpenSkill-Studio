"use client";

interface ScreenshotGalleryProps { screenshots: { url: string; alt?: string }[]; }

export function ScreenshotGallery({ screenshots }: ScreenshotGalleryProps) {
  if (screenshots.length === 0) return null;
  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {screenshots.map((s, i) => (
        <img key={i} src={s.url} alt={s.alt ?? `Screenshot ${i + 1}`}
          className="h-48 rounded-lg border border-gray-200 object-cover dark:border-gray-700" />
      ))}
    </div>
  );
}
