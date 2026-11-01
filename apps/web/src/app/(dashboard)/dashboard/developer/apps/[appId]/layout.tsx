"use client";

import Link from "next/link";
import { useParams, usePathname } from "next/navigation";

const cn = (...classes: (string | boolean | undefined)[]) => classes.filter(Boolean).join(" ");

export default function AppDetailLayout({ children }: { children: React.ReactNode }) {
  const { appId } = useParams<{ appId: string }>();
  const pathname = usePathname();
  const base = `/dashboard/developer/apps/${appId}`;

  const tabs = [
    { href: base, label: "Overview", exact: true },
    { href: `${base}/versions`, label: "Versions" },
    { href: `${base}/stats`, label: "Dashboard" },
    { href: `${base}/health`, label: "Health" },
    { href: `${base}/analytics`, label: "Analytics" },
    { href: `${base}/events`, label: "Events" },
    { href: `${base}/webhooks`, label: "Webhooks" },
    { href: `${base}/reviews`, label: "Reviews" },
    { href: `${base}/export`, label: "Export" },
    { href: `${base}/settings`, label: "Settings" },
  ];

  return (
    <div>
      {/* Back link */}
      <div className="border-b px-8 pt-4 dark:border-gray-700">
        <Link
          href="/dashboard/developer/apps"
          className="mb-3 inline-block text-sm text-blue-600 hover:underline"
        >
          ← All Apps
        </Link>

        {/* Tab navigation */}
        <div className="flex gap-1">
          {tabs.map((tab) => {
            const isActive = tab.exact
              ? pathname === tab.href
              : pathname.startsWith(tab.href);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  "rounded-t-lg border-b-2 px-4 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "border-blue-500 text-blue-600 dark:text-blue-400"
                    : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200",
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
