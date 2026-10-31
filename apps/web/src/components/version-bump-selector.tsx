"use client";

interface VersionBumpSelectorProps { currentVersion: string; onBump: (type: string) => void; }

const BUMPS = [
  { type: "patch", label: "Patch", desc: "Bug fixes", color: "bg-green-500" },
  { type: "minor", label: "Minor", desc: "New features", color: "bg-blue-500" },
  { type: "major", label: "Major", desc: "Breaking changes", color: "bg-red-500" },
];

export function VersionBumpSelector({ currentVersion, onBump }: VersionBumpSelectorProps) {
  const parts = currentVersion.split(".");
  const bumped = {
    patch: `${parts[0]}.${parts[1]}.${Number(parts[2]) + 1}`,
    minor: `${parts[0]}.${Number(parts[1]) + 1}.0`,
    major: `${Number(parts[0]) + 1}.0.0`,
  };
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏷️ Version Bump</h3>
        <div className="text-xs text-gray-400 mt-0.5">Current: v{currentVersion}</div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {BUMPS.map(b => (
          <button key={b.type} onClick={() => onBump(b.type)}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 text-left">
            <div>
              <div className="text-sm font-medium">{b.label}</div>
              <div className="text-[10px] text-gray-400">{b.desc}</div>
            </div>
            <span className="text-sm font-mono font-bold">v{bumped[b.type as keyof typeof bumped]}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
