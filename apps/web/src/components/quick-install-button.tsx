"use client";

interface QuickInstallButtonProps { quickInstall: boolean; stepsRequired: number; onInstall: () => void; loading?: boolean; }

export function QuickInstallButton({ quickInstall, stepsRequired, onInstall, loading }: QuickInstallButtonProps) {
  return (
    <button onClick={onInstall} disabled={loading}
      className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
      {loading ? "⏳ Installing..." : quickInstall ? "⚡ Install Now" : `📥 Install (${stepsRequired} steps)`}
    </button>
  );
}
