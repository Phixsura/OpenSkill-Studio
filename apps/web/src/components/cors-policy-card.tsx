"use client";

interface CORSPolicyInfo {
  policy_id: string;
  allowed_origins: string[];
  allowed_methods: string[];
  allowed_headers: string[];
  allow_credentials: boolean;
  max_age_seconds: number;
}

interface CORSPolicyCardProps {
  policies: CORSPolicyInfo[];
  appName: string;
}

export default function CORSPolicyCard({ policies, appName }: CORSPolicyCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🌍 CORS Policies
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{policies.length} policies</span>
      </div>

      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No CORS policies</p>
      ) : (
        <div className="space-y-2">
          {policies.map((p) => (
            <div
              key={p.policy_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {p.allowed_origins.includes("*")
                    ? "All origins (*)"
                    : `${p.allowed_origins.length} origins`}
                </span>
                {p.allow_credentials && (
                  <span className="rounded bg-yellow-100 px-1.5 py-0.5 text-[10px] text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300">
                    credentials
                  </span>
                )}
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {p.allowed_methods.map((m) => (
                  <span
                    key={m}
                    className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                  >
                    {m}
                  </span>
                ))}
              </div>
              <p className="mt-1 text-[10px] text-gray-400">max-age: {p.max_age_seconds}s</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
