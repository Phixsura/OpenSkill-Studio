"use client";

interface WidgetInfo {
  widget_id: string;
  widget_type: string;
  title: string;
  col: number;
  row: number;
  width: number;
  height: number;
}

interface LayoutInfo {
  layout_id: string;
  name: string;
  widgets: WidgetInfo[];
  is_default: boolean;
}

interface DashboardLayoutCardProps {
  layouts: LayoutInfo[];
  appName: string;
}

export default function DashboardLayoutCard({ layouts, appName }: DashboardLayoutCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🖥️ Dashboard Layouts
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{layouts.length} layouts</span>
      </div>

      {layouts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No layouts configured</p>
      ) : (
        <div className="space-y-2">
          {layouts.map((l) => (
            <div
              key={l.layout_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                    {l.name}
                  </span>
                  {l.is_default && (
                    <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                      Default
                    </span>
                  )}
                </div>
                <span className="text-[11px] text-gray-400">{l.widgets.length} widgets</span>
              </div>
              {l.widgets.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {l.widgets.slice(0, 4).map((w) => (
                    <span
                      key={w.widget_id}
                      className="rounded bg-gray-100 px-1.5 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                    >
                      {w.title || w.widget_type}
                    </span>
                  ))}
                  {l.widgets.length > 4 && (
                    <span className="text-[9px] text-gray-400">+{l.widgets.length - 4} more</span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
