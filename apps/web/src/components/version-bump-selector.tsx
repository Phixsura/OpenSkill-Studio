"use client";

interface VersionBumpSelectorProps { currentVersion: string; onSelect: (type: string, version: string) => void; }

export function VersionBumpSelector({ currentVersion, onSelect }: VersionBumpSelectorProps) {
  const parts = currentVersion.split(".").map(Number);
  const bumps = [
    { type: "patch", version: `${parts[0]}.${parts[1]}.${parts[2] + 1}`, label: "Patch", desc: "Bug fixes" },
    { type: "minor", version: `${parts[0]}.${parts[1] + 1}.0`, label: "Minor", desc: "New features" },
    { type: "major", version: `${parts[0] + 1}.0.0`, label: "Major", desc: "Breaking changes" },
  ];

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">Version Bump</label>
      <p className="text-xs text-gray-400">Current: {currentVersion}</p>
      <div className="flex gap-2">
        {bumps.map(b => (
          <button key={b.type} onClick={() => onSelect(b.type, b.version)}
            className="flex-1 rounded-lg border border-gray-200 p-3 text-left transition hover:border-blue-400 dark:border-gray-700">
            <p className="text-sm font-semibold">{b.label}</p>
            <p className="font-mono text-xs text-blue-600">{b.version}</p>
            <p className="text-xs text-gray-400">{b.desc}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
