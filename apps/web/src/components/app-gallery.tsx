"use client";

interface GalleryApp { id: string; name: string; icon: string; }
interface Collection { title: string; description: string; icon: string; apps: GalleryApp[]; }
interface AppGalleryProps { collections: Collection[]; onSelectApp: (id: string) => void; }

export function AppGallery({ collections, onSelectApp }: AppGalleryProps) {
  return (
    <div className="space-y-6">
      {collections.map(c => (
        <div key={c.title}>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xl">{c.icon}</span>
            <h3 className="text-lg font-bold">{c.title}</h3>
          </div>
          {c.description && <p className="text-sm text-gray-500 mb-3">{c.description}</p>}
          <div className="flex gap-3 overflow-x-auto pb-2">
            {c.apps.map(a => (
              <button key={a.id} onClick={() => onSelectApp(a.id)}
                className="flex shrink-0 flex-col items-center gap-1.5 rounded-xl border p-4 w-24 hover:shadow dark:border-gray-700">
                <span className="text-3xl">{a.icon}</span>
                <span className="text-xs font-medium truncate w-full text-center">{a.name}</span>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
