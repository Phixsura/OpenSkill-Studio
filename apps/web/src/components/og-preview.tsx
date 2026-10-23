"use client";

interface OgPreviewProps { title: string; description: string; url: string;
  image: string | null; siteName: string; }

export function OgPreview({ title, description, url, image, siteName }: OgPreviewProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Social Preview</h3>
      <div className="rounded-lg border overflow-hidden max-w-md dark:border-gray-700">
        {image && <div className="h-40 bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
          <img src={image} alt="" className="h-full w-full object-cover" />
        </div>}
        <div className="p-3">
          <p className="text-xs text-gray-400 uppercase">{siteName}</p>
          <h4 className="text-sm font-bold mt-0.5 line-clamp-1">{title}</h4>
          <p className="text-xs text-gray-500 line-clamp-2 mt-0.5">{description}</p>
          <p className="text-xs text-gray-400 mt-1 truncate">{url}</p>
        </div>
      </div>
    </div>
  );
}
