"use client";

interface PreferenceInfo {
  key: string;
  value: unknown;
  is_default: boolean;
  description: string;
}

interface UserPreferenceCardProps {
  preferences: PreferenceInfo[];
  userId: string;
  appName: string;
}

function formatValue(v: unknown): string {
  if (v === true) return "On";
  if (v === false) return "Off";
  if (v === null || v === undefined) return "—";
  return String(v);
}

export default function UserPreferenceCard({
  preferences,
  userId,
  appName,
}: UserPreferenceCardProps) {
  const customized = preferences.filter((p) => !p.is_default).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Preferences</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {userId}
          </p>
        </div>
        <span className="text-xs text-gray-400">{customized} customized</span>
      </div>

      {preferences.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No preferences</p>
      ) : (
        <div className="space-y-1.5">
          {preferences.map((p) => (
            <div
              key={p.key}
              className="flex items-center justify-between rounded px-2.5 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div>
                <span className="text-sm text-gray-800 dark:text-gray-200">
                  {p.key.replace(/_/g, " ")}
                </span>
                {p.description && <p className="text-[11px] text-gray-400">{p.description}</p>}
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`text-sm font-medium ${p.is_default ? "text-gray-400" : "text-blue-600 dark:text-blue-400"}`}
                >
                  {formatValue(p.value)}
                </span>
                {p.is_default && <span className="text-[10px] text-gray-400">default</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
