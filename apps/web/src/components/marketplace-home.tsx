"use client";

interface FeaturedExt { id: string; name: string; icon: string; tagline: string; }
interface HomeSection { id: string; title: string; type: string; items: { id: string; name: string; icon?: string; rating?: number; installs?: number }[]; }

export function MarketplaceHome({ featured, sections }: {
  featured: FeaturedExt[]; sections: HomeSection[];
}) {
  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-500 p-8 text-white text-center">
        <h1 className="text-3xl font-bold">🚀 Extension Marketplace</h1>
        <p className="text-lg mt-2 opacity-80">Discover, install, and build extensions for your platform</p>
      </div>

      {/* Featured */}
      {featured.length > 0 && (
        <div>
          <h2 className="text-lg font-bold mb-3">⭐ Featured</h2>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {featured.map((f) => (
              <div key={f.id} className="rounded-xl border-2 border-yellow-300 dark:border-yellow-700 p-4">
                <span className="text-3xl block mb-2">{f.icon}</span>
                <span className="font-bold">{f.name}</span>
                <p className="text-xs text-gray-500 mt-1">{f.tagline}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sections */}
      {sections.map((section) => (
        <div key={section.id}>
          <h2 className="text-lg font-bold mb-3">{section.title}</h2>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {section.items.slice(0, 8).map((item) => (
              <div key={item.id} className="rounded-xl border dark:border-gray-700 p-3 text-center hover:shadow transition">
                <span className="text-2xl block">{item.icon || "📦"}</span>
                <span className="font-semibold text-sm block mt-1">{item.name}</span>
                {item.rating && <span className="text-xs text-yellow-500">★ {item.rating}</span>}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
