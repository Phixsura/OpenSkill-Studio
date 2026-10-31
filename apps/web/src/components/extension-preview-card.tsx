"use client";

interface ExtPreview { name: string; icon: string; description: string; rating: number; installs: number; category: string; developer: string; }

export function ExtensionPreviewCard({ ext, onInstall }: { ext: ExtPreview; onInstall?: () => void }) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-4 hover:shadow-lg transition">
      <div className="flex items-center gap-3 mb-2">
        <span className="text-3xl">{ext.icon}</span>
        <div>
          <h3 className="font-bold">{ext.name}</h3>
          <span className="text-xs text-gray-500">by {ext.developer}</span>
        </div>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400">{ext.description}</p>
      <div className="flex items-center justify-between mt-3">
        <div className="flex gap-2 text-xs text-gray-500">
          <span className="text-yellow-500">★ {ext.rating}</span>
          <span>{ext.installs.toLocaleString()} installs</span>
          <span className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{ext.category}</span>
        </div>
        <button onClick={onInstall} className="text-sm bg-blue-600 text-white px-3 py-1 rounded-lg">Install</button>
      </div>
    </div>
  );
}
