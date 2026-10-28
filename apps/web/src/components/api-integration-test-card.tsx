"use client";

interface IntTestInfo {
  test_id: string;
  name: string;
  pass_count: number;
  fail_count: number;
  total_steps: number;
  passed: boolean | null;
}

interface APIIntegrationTestCardProps {
  tests: IntTestInfo[];
  appName: string;
}

export default function APIIntegrationTestCard({ tests, appName }: APIIntegrationTestCardProps) {
  const allPassed = tests.filter((t) => t.passed === true).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 Integration Tests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{allPassed}/{tests.length} passed</span>
      </div>

      {tests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No integration tests</p>
      ) : (
        <div className="space-y-1.5">
          {tests.map((t) => (
            <div key={t.test_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${t.passed === true ? "bg-green-500" : t.passed === false ? "bg-red-500" : "bg-gray-400"}`} />
                <span className="text-xs text-gray-700 dark:text-gray-300">{t.name}</span>
              </div>
              <span className="text-[10px] text-gray-400">{t.pass_count}/{t.total_steps} steps</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
