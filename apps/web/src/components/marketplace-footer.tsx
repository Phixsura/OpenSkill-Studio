"use client";
export function MarketplaceFooter({ version, year }: { version: string; year: number }) {
  return (
    <footer className="border-t dark:border-gray-700 py-4 text-center text-xs text-gray-500">
      <p>OpenSkill Developer Platform v{version} · © {year}</p>
      <div className="flex justify-center gap-4 mt-1">
        <span>Documentation</span><span>API Reference</span><span>Status</span><span>Support</span>
      </div>
    </footer>
  );
}
