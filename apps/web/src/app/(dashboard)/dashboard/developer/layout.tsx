"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const cn = (...classes: (string | boolean | undefined)[]) => classes.filter(Boolean).join(" ");

export default function DeveloperLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const base = "/dashboard/developer";

  const tabs = [
    { href: base, label: "Portal", exact: true },
    { href: `${base}/apps`, label: "My Apps" },
    { href: `${base}/keys`, label: "Keys" },
    { href: `${base}/docs`, label: "Docs" },
    { href: `${base}/tutorial`, label: "Tutorial" },
    { href: `${base}/api-reference`, label: "API" },
    { href: `${base}/settings`, label: "Settings" },
  ];

  return (
    <div>
      <div className="border-b bg-white px-8 pt-4 dark:border-gray-700 dark:bg-gray-900">
        <h2 className="mb-3 text-lg font-semibold">🧩 Developer Platform</h2>
        <div className="flex gap-1 overflow-x-auto">
          {tabs.map((tab) => {
            const isActive = tab.exact
              ? pathname === tab.href
              : pathname.startsWith(tab.href) && !tabs.some(
                  (t) => t !== tab && !t.exact && pathname.startsWith(t.href) && t.href.length > tab.href.length,
                );
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  "whitespace-nowrap rounded-t-lg border-b-2 px-4 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "border-blue-500 text-blue-600 dark:text-blue-400"
                    : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400",
                )}
              >
                {tab.label}
              </Link>
            );
          })}
        </div>
      </div>
      {children}
    </div>
  );
}
