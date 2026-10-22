"use client";

interface AppDetailHeaderProps {
  name: string;
  slug: string;
  category: string;
  status: string;
  iconUrl?: string | null;
  developerName?: string;
}

const CATEGORY_ICONS: Record<string, string> = {
  connector: "🔌", automation: "🤖", analytics: "📊", ui_extension: "🖥️",
  ecosystem_source: "🌐", content_pack: "📦", workflow_adapter: "⚡",
};

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800", published: "bg-green-100 text-green-800",
  deprecated: "bg-orange-100 text-orange-800", revoked: "bg-red-100 text-red-800",
};

export function AppDetailHeader({ name, slug, category, status, iconUrl, developerName }: AppDetailHeaderProps) {
  return (
    <div className="flex items-start gap-4">
      <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-gray-100 text-3xl dark:bg-gray-800">
        {iconUrl ? <img src={iconUrl} alt="" className="h-12 w-12 rounded-lg" /> : CATEGORY_ICONS[category] ?? "📦"}
      </div>
      <div>
        <h1 className="text-2xl font-bold">{name}</h1>
        <p className="text-sm text-gray-500">@{slug}{developerName ? ` · by ${developerName}` : ""}</p>
        <div className="mt-1 flex gap-2">
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[status] ?? "bg-gray-100"}`}>{status}</span>
          <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">{category.replace(/_/g, " ")}</span>
        </div>
      </div>
    </div>
  );
}
