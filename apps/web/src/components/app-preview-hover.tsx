"use client";

interface AppPreviewHoverProps { name: string; description: string; category: string; installs: number; health: number; visible: boolean; }

export function AppPreviewHover({ name, description, category, installs, health, visible }: AppPreviewHoverProps) {
  if (!visible) return null;
  return (
    <div className="absolute z-30 w-64 rounded-lg border border-gray-200 bg-white p-3 shadow-xl dark:border-gray-700 dark:bg-gray-900">
      <h4 className="font-semibold">{name}</h4>
      <p className="mt-1 text-xs text-gray-500 line-clamp-2">{description}</p>
      <div className="mt-2 flex gap-3 text-xs text-gray-400">
        <span>📥 {installs}</span><span>❤️ {health}%</span><span className="capitalize">{category}</span>
      </div>
    </div>
  );
}
