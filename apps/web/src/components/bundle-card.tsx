"use client";

interface Bundle { bundleId: string; name: string; description: string; extensions: string[]; discountPct: number; installCount: number; }

export function BundleCard({ bundle, onInstall }: { bundle: Bundle; onInstall?: (bundleId: string) => void }) {
  return (
    <div className="border dark:border-gray-700 rounded-xl p-4 space-y-3">
      <div className="flex justify-between items-start">
        <div>
          <span className="font-bold text-sm block">{bundle.name}</span>
          <p className="text-xs text-gray-500 mt-0.5">{bundle.description}</p>
        </div>
        {bundle.discountPct > 0 && (
          <span className="text-xs bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400 px-2 py-0.5 rounded-full font-medium">
            -{bundle.discountPct}%
          </span>
        )}
      </div>
      <div className="flex flex-wrap gap-1">
        {bundle.extensions.map(e => (
          <span key={e} className="text-xs bg-blue-50 dark:bg-blue-900/10 text-blue-600 px-2 py-0.5 rounded-full">{e}</span>
        ))}
      </div>
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-400">{bundle.installCount} installs · {bundle.extensions.length} extensions</span>
        <button onClick={() => onInstall?.(bundle.bundleId)} className="text-xs bg-blue-500 text-white px-3 py-1.5 rounded-lg">Install Bundle</button>
      </div>
    </div>
  );
}
