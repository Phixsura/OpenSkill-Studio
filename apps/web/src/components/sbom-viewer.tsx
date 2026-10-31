"use client";

interface SbomComponent { name: string; version: string; license: string; type: string; }
interface SbomViewerProps { appName: string; components: SbomComponent[];
  totalComponents: number; uniqueLicenses: string[]; compliant: boolean;
  violationCount: number; }

export function SbomViewer({ appName, components, totalComponents, uniqueLicenses, compliant, violationCount }: SbomViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">📋 SBOM: {appName}</h3>
          <div className="text-[10px] text-gray-400">{totalComponents} components · {uniqueLicenses.length} licenses</div>
        </div>
        <span className={`text-xs ${compliant ? "text-green-600" : "text-red-500"}`}>
          {compliant ? "✅ Compliant" : `⚠ ${violationCount} violations`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-48 overflow-y-auto">
        {components.map(c => (
          <div key={c.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-mono font-medium">{c.name}</span>
              <span className="text-gray-400">{c.version}</span>
            </div>
            <span className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-[10px]">{c.license}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
