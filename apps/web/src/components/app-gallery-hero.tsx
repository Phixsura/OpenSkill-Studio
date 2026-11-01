"use client";

interface GalleryApp { id: string; name: string; }
interface GallerySection { id: string; title: string; icon: string; apps: GalleryApp[]; }
interface Collection { id: string; title: string; description: string; app_count: number; icon: string; }
interface AppGalleryHeroProps { sections: GallerySection[]; collections: Collection[];
  onAppClick: (id: string) => void; onCollectionClick: (id: string) => void; }

export function AppGalleryHero({ sections, collections, onAppClick, onCollectionClick }: AppGalleryHeroProps) {
  return (
    <div className="space-y-8">
      {sections.map(s => (
        <div key={s.id}>
          <h2 className="flex items-center gap-2 text-xl font-bold">
            <span>{s.icon}</span> {s.title}
          </h2>
          <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
            {s.apps.map(app => (
              <button key={app.id} onClick={() => onAppClick(app.id)}
                className="rounded-lg border p-3 text-left hover:border-blue-400 dark:border-gray-700">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 text-lg text-white">
                  {app.name.charAt(0)}
                </div>
                <p className="mt-2 text-sm font-medium">{app.name}</p>
              </button>
            ))}
          </div>
        </div>
      ))}
      {collections.length > 0 && (
        <div>
          <h2 className="text-xl font-bold">📚 Collections</h2>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {collections.map(c => (
              <button key={c.id} onClick={() => onCollectionClick(c.id)}
                className="flex items-center gap-3 rounded-lg border p-4 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
                <span className="text-2xl">{c.icon}</span>
                <div>
                  <p className="font-semibold">{c.title}</p>
                  <p className="text-xs text-gray-400">{c.app_count} apps · {c.description}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
