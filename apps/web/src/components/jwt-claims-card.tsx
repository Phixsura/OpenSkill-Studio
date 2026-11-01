"use client";

interface JWTValidationInfo {
  valid: boolean;
  claims: Record<string, unknown>;
  errors: string[];
  issuer: string;
  audience: string;
  expired: boolean;
}

interface JWTClaimsCardProps {
  validation: JWTValidationInfo;
  appName: string;
}

export default function JWTClaimsCard({ validation: v, appName }: JWTClaimsCardProps) {
  const claimKeys = Object.keys(v.claims);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">JWT Claims</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {v.valid ? (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            ✓ Valid
          </span>
        ) : (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            ✕ Invalid
          </span>
        )}
      </div>

      {/* Errors */}
      {v.errors.length > 0 && (
        <div className="mb-3 space-y-1">
          {v.errors.map((e, i) => (
            <p key={i} className="text-xs text-red-500">
              • {e}
            </p>
          ))}
        </div>
      )}

      {/* Claims */}
      {claimKeys.length > 0 ? (
        <div className="rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
          <div className="space-y-0.5">
            {claimKeys.map((k) => (
              <div key={k} className="flex items-center justify-between font-mono text-[11px]">
                <span className="text-gray-600 dark:text-gray-400">{k}</span>
                <span className="max-w-[200px] truncate text-gray-800 dark:text-gray-200">
                  {JSON.stringify(v.claims[k])}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-center text-sm text-gray-400">No claims</p>
      )}
    </div>
  );
}
