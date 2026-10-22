"use client";

interface DeveloperVerificationStatusProps {
  verified: boolean;
  email: string;
  onVerify?: () => void;
}

export function DeveloperVerificationStatus({ verified, email, onVerify }: DeveloperVerificationStatusProps) {
  return (
    <div className={`rounded-lg border p-4 ${verified ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20" : "border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20"}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">{verified ? "✅" : "⚠️"}</span>
          <div>
            <p className="font-semibold">{verified ? "Verified Developer" : "Unverified"}</p>
            <p className="text-xs text-gray-500">{email}</p>
          </div>
        </div>
        {!verified && onVerify && (
          <button onClick={onVerify} className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700">Verify Now</button>
        )}
      </div>
    </div>
  );
}
