"use client";

import { useState } from "react";

interface ShareStats { views: number; installs: number; conversionRate: number; }
interface SocialUrls { twitter: string; linkedin: string; copyLink: string; }

export function ExtensionSharePanel({ shareUrl, embedCode, stats, social, onCopyLink }: {
  shareUrl: string; embedCode: string; stats: ShareStats; social: SocialUrls;
  onCopyLink?: () => void;
}) {
  const [tab, setTab] = useState<"link" | "embed" | "social">("link");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📤 Share Extension</h2>

      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="font-bold text-lg">{stats.views}</span>
          <span className="text-gray-500 block">Views</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="font-bold text-lg text-green-600">{stats.installs}</span>
          <span className="text-gray-500 block">Installs</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="font-bold text-lg text-blue-600">{stats.conversionRate}%</span>
          <span className="text-gray-500 block">Conversion</span>
        </div>
      </div>

      <div className="flex gap-1">
        {(["link", "embed", "social"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "link" ? "🔗 Link" : t === "embed" ? "📋 Embed" : "📱 Social"}
          </button>
        ))}
      </div>

      {tab === "link" && (
        <div className="flex gap-2">
          <code className="flex-1 bg-gray-50 dark:bg-gray-900 rounded-lg px-3 py-2 text-xs overflow-hidden">{shareUrl}</code>
          <button onClick={onCopyLink} className="text-sm bg-blue-600 text-white px-3 py-2 rounded-lg">Copy</button>
        </div>
      )}

      {tab === "embed" && (
        <pre className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 text-xs overflow-x-auto">{embedCode}</pre>
      )}

      {tab === "social" && (
        <div className="flex gap-2">
          <a href={social.twitter} className="flex-1 text-center text-sm bg-blue-400 text-white py-2 rounded-lg">🐦 Twitter</a>
          <a href={social.linkedin} className="flex-1 text-center text-sm bg-blue-700 text-white py-2 rounded-lg">💼 LinkedIn</a>
        </div>
      )}
    </div>
  );
}
