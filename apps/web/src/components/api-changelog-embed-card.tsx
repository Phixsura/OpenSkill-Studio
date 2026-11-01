"use client";
interface EmbedInfo { theme: string; max_entries: number; show_reactions: boolean; }
interface APIChangelogEmbedCardProps { config: EmbedInfo; appName: string; }

export default function APIChangelogEmbedCard({ config, appName }: APIChangelogEmbedCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🖼️ Changelog Embed</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="space-y-1 text-[11px]">
        <div className="flex justify-between"><span className="text-gray-500">Theme</span><span className="text-gray-700 dark:text-gray-300">{config.theme}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Max entries</span><span className="text-gray-700 dark:text-gray-300">{config.max_entries}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Reactions</span><span className="text-gray-700 dark:text-gray-300">{config.show_reactions ? "on" : "off"}</span></div>
      </div>
    </div>
  );
}
