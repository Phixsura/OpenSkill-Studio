"use client";

interface HeroStats {
  extensions: number;
  developers: number;
  installs: number;
  categories: number;
}

export function MarketplaceOverviewHero({
  stats,
  onBrowse,
  onPublish,
}: {
  stats: HeroStats;
  onBrowse?: () => void;
  onPublish?: () => void;
}) {
  return (
    <div className="rounded-2xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 p-8 text-white">
      <div className="max-w-2xl mx-auto text-center space-y-4">
        <h1 className="text-3xl md:text-4xl font-black">
          🏪 OpenSkill Marketplace
        </h1>
        <p className="text-lg text-blue-100">
          Discover, install, and build extensions for the OpenSkill platform
        </p>

        <div className="grid grid-cols-4 gap-4 py-4">
          <StatBubble value={stats.extensions} label="Extensions" />
          <StatBubble value={stats.developers} label="Developers" />
          <StatBubble value={stats.installs} label="Installs" />
          <StatBubble value={stats.categories} label="Categories" />
        </div>

        <div className="flex justify-center gap-3 pt-2">
          <button onClick={onBrowse}
            className="rounded-xl bg-white text-blue-700 px-6 py-3 font-bold text-sm hover:bg-blue-50 transition">
            🔍 Browse Extensions
          </button>
          <button onClick={onPublish}
            className="rounded-xl bg-white/20 text-white px-6 py-3 font-bold text-sm hover:bg-white/30 transition border border-white/30">
            📦 Publish Yours
          </button>
        </div>
      </div>
    </div>
  );
}

function StatBubble({ value, label }: { value: number; label: string }) {
  return (
    <div className="bg-white/10 rounded-xl p-3">
      <div className="text-2xl font-black">{value.toLocaleString()}</div>
      <div className="text-xs text-blue-200">{label}</div>
    </div>
  );
}
