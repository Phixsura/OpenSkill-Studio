"use client";

interface MarketplacePageLayoutProps { activePage: string; children: React.ReactNode; }

export function MarketplacePageLayout({ activePage, children }: MarketplacePageLayoutProps) {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <header className="mb-6">
        <a href="/marketplace" className="text-xl font-bold">📦 OpenSkill Marketplace</a>
      </header>
      <main>{children}</main>
      <footer className="mt-12 border-t pt-6 text-center text-xs text-gray-400">© 2026 OpenSkill Studio</footer>
    </div>
  );
}
