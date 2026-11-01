"use client";

interface PlatformStatsFooterProps { commits: number; lines: number; files: number;
  services: number; modules: number; status: string; }

export function PlatformStatsFooter({ commits, lines, files, services, modules, status }: PlatformStatsFooterProps) {
  return (
    <div className="border-t dark:border-gray-700 mt-12 py-6 text-center">
      <div className="flex justify-center gap-6 text-xs text-gray-400 mb-2">
        <span>📊 {commits.toLocaleString()} commits</span>
        <span>📝 {lines.toLocaleString()} lines</span>
        <span>📁 {files.toLocaleString()} files</span>
        <span>⚙️ {services.toLocaleString()} services</span>
        <span>📦 {modules} modules</span>
      </div>
      <p className="text-xs text-green-600 font-medium">✅ {status}</p>
      <p className="text-xs text-gray-300 mt-1">Built with Claude Opus 5 (1M context)</p>
    </div>
  );
}
