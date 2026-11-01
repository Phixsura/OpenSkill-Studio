"use client";

interface TestCaseInfo {
  test_id: string;
  name: string;
  method: string;
  path: string;
  result: "pending" | "passed" | "failed" | "skipped";
}

interface TestSuiteInfo {
  suite_id: string;
  name: string;
  tests: TestCaseInfo[];
  pass_rate: number;
}

interface APITestSuiteCardProps {
  suites: TestSuiteInfo[];
  appName: string;
}

const resultDot: Record<string, string> = {
  pending: "bg-gray-400",
  passed: "bg-green-500",
  failed: "bg-red-500",
  skipped: "bg-yellow-500",
};

export default function APITestSuiteCard({ suites, appName }: APITestSuiteCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🧪 API Test Suites
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{suites.length} suites</span>
      </div>

      {suites.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No test suites</p>
      ) : (
        <div className="space-y-3">
          {suites.map((s) => (
            <div
              key={s.suite_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {s.name}
                </span>
                <span
                  className={`text-[11px] font-medium ${s.pass_rate >= 100 ? "text-green-600" : s.pass_rate >= 50 ? "text-yellow-600" : "text-red-500"}`}
                >
                  {s.pass_rate}% pass
                </span>
              </div>
              <div className="mt-1 space-y-0.5">
                {s.tests.map((t) => (
                  <div key={t.test_id} className="flex items-center gap-1.5 text-[10px]">
                    <span className={`h-1.5 w-1.5 rounded-full ${resultDot[t.result]}`} />
                    <span className="text-gray-500">{t.name}</span>
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
