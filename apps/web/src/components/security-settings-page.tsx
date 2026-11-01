"use client";

interface SecuritySetting { key: string; label: string; icon: string; description: string;
  enabled?: boolean; value?: number; type: string; unit?: string; }
interface SecuritySettingsPageProps { settings: SecuritySetting[]; securityScore: number;
  grade: string; onToggle: (key: string) => void; }

const gradeColors: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600" };

export function SecuritySettingsPage({ settings, securityScore, grade, onToggle }: SecuritySettingsPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔒 Security Settings</h2>
        <div className="flex items-center gap-2">
          <span className={`text-2xl font-bold ${gradeColors[grade] ?? ""}`}>{grade}</span>
          <span className="text-xs text-gray-400">{securityScore}%</span>
        </div>
      </div>
      <div className="space-y-2">
        {settings.map(s => (
          <div key={s.key} className="flex items-center justify-between rounded-xl border px-4 py-3 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <span className="text-xl">{s.icon}</span>
              <div>
                <p className="text-sm font-medium">{s.label}</p>
                <p className="text-xs text-gray-400">{s.description}</p>
              </div>
            </div>
            {s.type === "toggle" ? (
              <button onClick={() => onToggle(s.key)}
                className={`relative h-6 w-11 rounded-full transition ${s.enabled ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}>
                <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition ${s.enabled ? "left-[22px]" : "left-0.5"}`} />
              </button>
            ) : (
              <span className="text-sm text-gray-500">{s.value} {s.unit}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
