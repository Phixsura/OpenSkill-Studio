"use client";

interface EnvConfigSwitcherProps { activeEnv: string; onSwitch: (env: string) => void; envs?: string[]; }

const ENV_STYLES: Record<string, { color: string; icon: string }> = {
  development: { color: "bg-green-100 text-green-700", icon: "🛠️" },
  staging: { color: "bg-yellow-100 text-yellow-700", icon: "🔄" },
  production: { color: "bg-red-100 text-red-700", icon: "🚀" },
};

export function EnvConfigSwitcher({ activeEnv, onSwitch, envs = ["development", "staging", "production"] }: EnvConfigSwitcherProps) {
  return (
    <div className="flex gap-2">
      {envs.map(env => {
        const style = ENV_STYLES[env] || { color: "bg-gray-100", icon: "⚙️" };
        return (
          <button key={env} onClick={() => onSwitch(env)}
            className={`rounded-lg px-3 py-2 text-sm transition ${activeEnv === env ? `${style.color} font-semibold ring-2 ring-offset-1` : "bg-gray-50 text-gray-500 dark:bg-gray-800"}`}>
            {style.icon} {env.charAt(0).toUpperCase() + env.slice(1)}
          </button>
        );
      })}
    </div>
  );
}
