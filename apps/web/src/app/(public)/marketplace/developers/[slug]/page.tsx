"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

interface DeveloperProfile {
  id: string;
  display_name: string;
  slug: string;
  website_url: string | null;
  verified: boolean;
}

interface DeveloperApp {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon_url: string | null;
  category: string;
  install_count: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

const CATEGORY_ICONS: Record<string, string> = {
  connector: "🔌",
  workflow_adapter: "⚡",
  ui_extension: "🖥️",
  analytics: "📊",
  automation: "🤖",
  content_pack: "📦",
  ecosystem_source: "🌐",
};

export default function DeveloperProfilePage() {
  const { slug } = useParams<{ slug: string }>();

  // TODO: Add public developer profile API endpoint
  // For now, show a placeholder with the slug
  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <Link
          href="/marketplace/apps"
          className="text-sm text-blue-600 hover:underline"
        >
          ← Back to Marketplace
        </Link>
      </div>

      <div className="mb-8 flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-2xl font-bold text-white">
          {slug.charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 className="text-2xl font-bold">{slug}</h1>
          <p className="text-gray-500 dark:text-gray-400">@{slug}</p>
        </div>
      </div>

      <div className="rounded-lg border p-8 text-center dark:border-gray-700">
        <p className="text-gray-500 dark:text-gray-400">
          Developer profile pages coming soon.
        </p>
        <p className="mt-2 text-sm text-gray-400">
          Browse their published apps in the{" "}
          <Link href="/marketplace/apps" className="text-blue-600 hover:underline">
            marketplace
          </Link>
          .
        </p>
      </div>
    </div>
  );
}
