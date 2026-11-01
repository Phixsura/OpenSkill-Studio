"use client";

interface Screenshot { id: string; url: string; position: number; }
interface ScreenshotGalleryEditorProps { screenshots: Screenshot[]; onReorder: (ids: string[]) => void; onDelete: (id: string) => void; onUpload: () => void; }

export function ScreenshotGalleryEditor({ screenshots, onReorder, onDelete, onUpload }: ScreenshotGalleryEditorProps) {
  const sorted = [...screenshots].sort((a, b) => a.position - b.position);
  const moveUp = (idx: number) => {
    if (idx === 0) return;
    const ids = sorted.map(s => s.id);
    [ids[idx - 1], ids[idx]] = [ids[idx], ids[idx - 1]];
    onReorder(ids);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Screenshots</h2>
        <button onClick={onUpload} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Upload</button>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {sorted.map((s, i) => (
          <div key={s.id} className="group relative rounded-lg border dark:border-gray-700">
            <div className="aspect-video rounded-t-lg bg-gray-100 dark:bg-gray-800">
              <p className="flex h-full items-center justify-center text-xs text-gray-400">{s.url}</p>
            </div>
            <div className="flex justify-between p-1.5">
              <button onClick={() => moveUp(i)} disabled={i === 0}
                className="text-xs text-gray-400 disabled:opacity-30">↑ Move up</button>
              <button onClick={() => onDelete(s.id)} className="text-xs text-red-500">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
