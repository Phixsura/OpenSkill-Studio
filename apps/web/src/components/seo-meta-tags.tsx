"use client";

interface SeoMeta { title: string; description: string; url: string; image?: string; type?: string; }

export function SeoMetaTags({ meta }: { meta: SeoMeta }) {
  return (
    <div className="border dark:border-gray-700 rounded-xl p-4 space-y-2">
      <h3 className="font-bold text-sm">SEO Preview</h3>
      <div className="bg-white dark:bg-gray-900 rounded-lg border dark:border-gray-700 p-3 space-y-1">
        <span className="text-blue-600 text-sm font-medium block truncate">{meta.title}</span>
        <span className="text-xs text-green-700 block truncate">{meta.url}</span>
        <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">{meta.description}</p>
      </div>
      <div className="text-xs text-gray-500 space-y-0.5">
        <div>Title: {meta.title.length}/60 chars {meta.title.length > 60 && "⚠️"}</div>
        <div>Description: {meta.description.length}/160 chars {meta.description.length > 160 && "⚠️"}</div>
      </div>
    </div>
  );
}
