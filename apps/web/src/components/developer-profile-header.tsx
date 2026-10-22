"use client";

interface DeveloperProfileHeaderProps { name: string; verified: boolean; appCount: number; totalInstalls: number; categories: string[]; }

export function DeveloperProfileHeader({ name, verified, appCount, totalInstalls, categories }: DeveloperProfileHeaderProps) {
  return (
    <div className="rounded-xl bg-gradient-to-r from-gray-800 to-gray-900 p-6 text-white">
      <div className="flex items-center gap-2">
        <h1 className="text-2xl font-bold">{name}</h1>
        {verified && <span className="rounded-full bg-blue-500 px-2 py-0.5 text-xs">✓ Verified</span>}
      </div>
      <div className="mt-2 flex gap-4 text-sm opacity-80">
        <span>📦 {appCount} apps</span>
        <span>📥 {totalInstalls} installs</span>
        <span>{categories.join(" · ")}</span>
      </div>
    </div>
  );
}
