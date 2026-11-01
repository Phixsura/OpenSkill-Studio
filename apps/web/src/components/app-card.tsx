"use client";

import Link from "next/link";
import { AppStatusBadge } from "./app-status-badge";

interface AppCardProps {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  category: string;
  status: string;
  installCount?: number;
  developerName?: string | null;
  href?: string;
}

const CATEGORY_ICONS: Record<string, string> = {
  connector: "🔌", CONNECTOR: "🔌",
  workflow_adapter: "⚡", WORKFLOW_ADAPTER: "⚡",
  ui_extension: "🖥️", UI_EXTENSION: "🖥️",
  analytics: "📊", ANALYTICS: "📊",
  automation: "🤖", AUTOMATION: "🤖",
  content_pack: "📦", CONTENT_PACK: "📦",
  ecosystem_source: "🌐", ECOSYSTEM_SOURCE: "🌐",
};

export function AppCard({
  id, name, slug, description, category, status,
  installCount, developerName, href,
}: AppCardProps) {
  const link = href ?? `/marketplace/apps/${id}`;
  const icon = CATEGORY_ICONS[category] ?? "📦";

  return (
    <Link
      href={link}
      className="group block rounded-xl border p-5 transition-all hover:border-blue-500 hover:shadow-md dark:border-gray-700"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-gray-100 text-xl dark:bg-gray-700">
          {icon}
        </div>
        <div className="flex-1 overflow-hidden">
          <div className="flex items-center gap-2">
            <h3 className="truncate font-semibold group-hover:text-blue-600">{name}</h3>
            <AppStatusBadge status={status} />
          </div>
          {developerName && (
            <p className="text-xs text-gray-500">by {developerName}</p>
          )}
        </div>
      </div>
      {description && (
        <p className="mt-2 text-sm text-gray-600 line-clamp-2 dark:text-gray-300">
          {description}
        </p>
      )}
      <div className="mt-3 flex items-center justify-between text-xs text-gray-400">
        <span>{category.replace("_", " ")}</span>
        {installCount !== undefined && (
          <span>{installCount} install{installCount !== 1 ? "s" : ""}</span>
        )}
      </div>
    </Link>
  );
}
