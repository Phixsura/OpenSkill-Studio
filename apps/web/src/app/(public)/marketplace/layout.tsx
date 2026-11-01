"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function MarketplaceLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <main id="main-content">
      {/* Marketplace navigation bar */}
      <nav className="border-b bg-white dark:border-gray-800 dark:bg-gray-900">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-6">
            <Link href="/" className="text-lg font-bold">
              OpenSkill
            </Link>
            <div className="flex gap-4">
              <Link
                href="/registry"
                className={`text-sm font-medium ${
                  pathname.startsWith("/registry")
                    ? "text-blue-600 dark:text-blue-400"
                    : "text-gray-500 hover:text-gray-700 dark:text-gray-400"
                }`}
              >
                📦 Skill Packs
              </Link>
              <Link
                href="/marketplace/apps"
                className={`text-sm font-medium ${
                  pathname.startsWith("/marketplace/apps")
                    ? "text-blue-600 dark:text-blue-400"
                    : "text-gray-500 hover:text-gray-700 dark:text-gray-400"
                }`}
              >
                🧩 Apps
              </Link>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard/developer"
              className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400"
            >
              Build an App →
            </Link>
            <Link
              href="/login"
              className="rounded-lg bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
            >
              Sign In
            </Link>
          </div>
        </div>
      </nav>
      {children}
    </main>
  );
}
