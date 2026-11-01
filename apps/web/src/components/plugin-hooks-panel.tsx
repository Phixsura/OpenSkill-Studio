"use client";

interface HookRegistration {
  id: string;
  hookPoint: string;
  handlerName: string;
  priority: number;
  enabled: boolean;
  errorCount: number;
  maxErrors: number;
}

const hookPointLabels: Record<string, string> = {
  pre_install: "Pre Install", post_install: "Post Install",
  pre_activate: "Pre Activate", post_activate: "Post Activate",
  pre_deactivate: "Pre Deactivate", post_deactivate: "Post Deactivate",
  pre_update: "Pre Update", post_update: "Post Update",
  pre_uninstall: "Pre Uninstall", post_uninstall: "Post Uninstall",
  on_error: "On Error", on_config_change: "Config Change",
};

export function PluginHooksPanel({
  hooks,
  extensionName,
  onToggle,
  onRemove,
}: {
  hooks: HookRegistration[];
  extensionName: string;
  onToggle?: (id: string) => void;
  onRemove?: (id: string) => void;
}) {
  const active = hooks.filter((h) => h.enabled).length;
  const grouped = hooks.reduce<Record<string, HookRegistration[]>>((acc, h) => {
    (acc[h.hookPoint] ||= []).push(h);
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🪝 {extensionName} Hooks</h2>
        <span className="text-sm text-gray-500">{active}/{hooks.length} active</span>
      </div>

      {Object.entries(grouped).map(([point, pointHooks]) => (
        <div key={point}>
          <span className="text-xs font-semibold text-gray-500 uppercase">{hookPointLabels[point] || point}</span>
          <div className="mt-1 space-y-1">
            {pointHooks.sort((a, b) => b.priority - a.priority).map((h) => (
              <div key={h.id} className={`rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between ${!h.enabled ? "opacity-50" : ""}`}>
                <div className="flex items-center gap-2">
                  <code className="text-sm">{h.handlerName}</code>
                  <span className="text-xs text-gray-400">P{h.priority}</span>
                  {h.errorCount > 0 && (
                    <span className="text-xs text-red-500">{h.errorCount}/{h.maxErrors} errors</span>
                  )}
                </div>
                <div className="flex gap-1">
                  <button onClick={() => onToggle?.(h.id)}
                    className={`text-xs px-2 py-1 rounded ${h.enabled ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
                    {h.enabled ? "On" : "Off"}
                  </button>
                  <button onClick={() => onRemove?.(h.id)}
                    className="text-xs text-red-500 hover:text-red-700">✕</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
