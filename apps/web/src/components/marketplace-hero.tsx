"use client";
export function MarketplaceHero({ title, subtitle, extensionCount }: { title: string; subtitle: string; extensionCount: number }) {
  return (
    <div className="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 p-8 text-white text-center">
      <h1 className="text-3xl font-bold">{title}</h1>
      <p className="text-lg opacity-80 mt-2">{subtitle}</p>
      <span className="inline-block mt-4 bg-white/20 rounded-full px-4 py-1 text-sm">{extensionCount.toLocaleString()} extensions available</span>
    </div>
  );
}
