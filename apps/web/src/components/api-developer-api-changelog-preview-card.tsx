"use client";

interface PreviewInfo { preview_id: string; version: string; title: string; entry_count: number; published: boolean; reviewer: string; }
interface Props { previews: PreviewInfo[]; appName: string; }

export default function APIDeveloperAPIChangelogPreviewCard({ previews, appName }: Props) {
  const drafts = previews.filter((p) => !p.published).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👁️ Changelog Previews</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{drafts} drafts / {previews.length} total</span>
      </div>
      {previews.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No previews</p>
      ) : (
        <div className="space-y-1.5">
          {previews.map((p) => (
            <div key={p.preview_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${p.published ? "bg-green-500" : p.reviewer ? "bg-yellow-500" : "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{p.title}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{p.version}</span>
              </div>
              <span className="text-gray-400">{p.entry_count} entries</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
