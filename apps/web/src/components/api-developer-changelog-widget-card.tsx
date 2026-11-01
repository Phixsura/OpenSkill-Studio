"use client";

interface WidgetInfo { position: string; trigger: string; max_items: number; theme: string; impressions: number; clicks: number; ctr: number; }
interface Props { widget: WidgetInfo | null; appName: string; }

export default function APIDeveloperChangelogWidgetCard({ widget, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Changelog Widget</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      {!widget ? (
        <p className="text-center text-sm text-gray-400">Widget not configured</p>
      ) : (
        <div className="space-y-2">
          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div><span className="text-gray-500">Position:</span> <span className="text-gray-700 dark:text-gray-300">{widget.position}</span></div>
            <div><span className="text-gray-500">Trigger:</span> <span className="text-gray-700 dark:text-gray-300">{widget.trigger}</span></div>
            <div><span className="text-gray-500">Theme:</span> <span className="text-gray-700 dark:text-gray-300">{widget.theme}</span></div>
            <div><span className="text-gray-500">Items:</span> <span className="text-gray-700 dark:text-gray-300">{widget.max_items}</span></div>
          </div>
          <div className="flex justify-between text-[10px] text-gray-400">
            <span>{widget.impressions} impressions</span>
            <span>{widget.clicks} clicks</span>
            <span>{widget.ctr}% CTR</span>
          </div>
        </div>
      )}
    </div>
  );
}
