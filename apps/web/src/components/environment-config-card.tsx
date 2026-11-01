"use client";

interface EnvironmentInfo {
  env_id: string;
  name: string;
  setting_count: number;
  locked: boolean;
}

interface EnvironmentConfigCardProps {
  environments: EnvironmentInfo[];
  appName: string;
}

const ENV_COLORS: Record<string, string> = {
  dev: "border-green-400 dark:border-green-500",
  staging: "border-yellow-400 dark:border-yellow-500",
  prod: "border-red-400 dark:border-red-500",
  production: "border-red-400 dark:border-red-500",
};

export default function EnvironmentConfigCard({
  environments,
  appName,
}: EnvironmentConfigCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Environments</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{environments.length} environments</span>
      </div>

      {environments.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No environments</p>
      ) : (
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          {environments.map((e) => {
            const border = ENV_COLORS[e.env_id] ?? "border-gray-300 dark:border-gray-600";
            return (
              <div key={e.env_id} className={`rounded-lg border-2 px-3 py-2.5 ${border}`}>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                    {e.name}
                  </span>
                  {e.locked && <span className="text-[10px] text-red-500">🔒 locked</span>}
                </div>
                <div className="mt-1 text-[11px] text-gray-400">{e.setting_count} settings</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
