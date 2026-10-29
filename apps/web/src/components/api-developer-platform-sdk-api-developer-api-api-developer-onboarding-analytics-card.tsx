"use client";

interface AnalyticsInfo { total_started: number; total_completed: number; completion_rate: number; avg_time_to_first_call_hours: number; drop_off_step: string; quality: string; }
interface Props { analytics: AnalyticsInfo; appName: string; }

const qColor: Record<string, string> = { excellent: "text-green-600", good: "text-blue-600", needs_improvement: "text-yellow-600", poor: "text-red-600" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperOnboardingAnalyticsCard({ analytics: a, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎓 Onboarding Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${qColor[a.quality] ?? ""}`}>{a.completion_rate}%</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-center">
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-blue-600">{a.total_started}</p>
          <p className="text-[9px] text-gray-400">Started</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-green-600">{a.total_completed}</p>
          <p className="text-[9px] text-gray-400">Completed</p>
        </div>
      </div>
      <div className="mt-2 flex justify-between text-[10px] text-gray-400">
        <span>First call: {a.avg_time_to_first_call_hours}h</span>
        {a.drop_off_step && <span>Drop-off: {a.drop_off_step}</span>}
      </div>
    </div>
  );
}
