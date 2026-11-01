"use client";

interface VariantInfo { name: string; weight: number; impressions: number; conversions: number; conversion_rate: number; }
interface TestInfo { test_id: string; endpoint: string; status: string; variants: VariantInfo[]; winner: string | null; }
interface Props { tests: TestInfo[]; appName: string; }

export default function APIDeveloperAPIApiABTestManagerCard({ tests, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 A/B Tests</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {tests.length} experiments</p>
      </div>
      {tests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No A/B tests</p>
      ) : (
        <div className="space-y-3">
          {tests.map((t) => (
            <div key={t.test_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{t.endpoint}</span>
                <span className={`rounded px-1 py-0.5 text-[9px] ${t.status === "running" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>{t.status}</span>
              </div>
              <div className="mt-1 space-y-0.5">
                {t.variants.map((v) => (
                  <div key={v.name} className="flex items-center justify-between text-[10px]">
                    <span className={`text-gray-600 dark:text-gray-400 ${t.winner === v.name ? "font-bold text-green-600" : ""}`}>{v.name} ({v.weight}%)</span>
                    <span className="text-gray-400">{v.conversion_rate}% CVR · {v.impressions} imp</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
