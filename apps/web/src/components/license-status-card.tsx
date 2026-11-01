"use client";

interface LicenseData {
  license_key: string;
  app_name: string;
  license_type: "perpetual" | "subscription" | "trial" | "site";
  status: "active" | "expired" | "grace" | "revoked" | "trial_active" | "trial_expired";
  max_seats: number;
  active_seats: number;
  days_remaining: number | null;
  issued_at: string;
  expires_at: string | null;
}

interface LicenseStatusCardProps {
  license: LicenseData;
  onDeactivate: () => void;
  onRenew: () => void;
}

const STATUS_STYLES: Record<string, { label: string; color: string }> = {
  active: {
    label: "Active",
    color: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300",
  },
  trial_active: {
    label: "Trial",
    color: "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300",
  },
  grace: {
    label: "Grace Period",
    color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300",
  },
  expired: {
    label: "Expired",
    color: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300",
  },
  trial_expired: {
    label: "Trial Expired",
    color: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300",
  },
  revoked: {
    label: "Revoked",
    color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  },
};

const TYPE_LABELS: Record<string, string> = {
  perpetual: "Perpetual",
  subscription: "Subscription",
  trial: "Trial",
  site: "Site License",
};

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return iso;
  }
}

export function LicenseStatusCard({ license, onDeactivate, onRenew }: LicenseStatusCardProps) {
  const st = STATUS_STYLES[license.status] ?? STATUS_STYLES.expired;
  const isValid = ["active", "trial_active", "grace"].includes(license.status);
  const seatsUsed = license.active_seats;
  const seatsPct = license.max_seats > 0 ? Math.round((seatsUsed / license.max_seats) * 100) : 0;

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div>
          <h3 className="font-semibold">{license.app_name}</h3>
          <p className="text-xs text-gray-500">
            {TYPE_LABELS[license.license_type] ?? license.license_type} License
          </p>
        </div>
        <span className={`rounded-full px-2.5 py-0.5 text-[10px] font-semibold ${st.color}`}>
          {st.label}
        </span>
      </div>

      {/* Key */}
      <div className="border-b border-gray-200 px-4 py-2 dark:border-gray-700">
        <p className="text-[10px] text-gray-400">License Key</p>
        <code className="text-xs font-medium">{license.license_key}</code>
      </div>

      {/* Details grid */}
      <div className="grid grid-cols-3 gap-3 px-4 py-3">
        <div>
          <p className="text-[10px] text-gray-500">Seats</p>
          <p className="text-sm font-bold">
            {seatsUsed}/{license.max_seats}
          </p>
          <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
            <div
              className={`h-full rounded-full ${seatsPct >= 90 ? "bg-red-500" : "bg-blue-500"}`}
              style={{ width: `${Math.min(seatsPct, 100)}%` }}
            />
          </div>
        </div>
        <div>
          <p className="text-[10px] text-gray-500">Issued</p>
          <p className="text-sm font-medium">{formatDate(license.issued_at)}</p>
        </div>
        <div>
          <p className="text-[10px] text-gray-500">{license.expires_at ? "Expires" : "Expiry"}</p>
          <p className="text-sm font-medium">
            {license.expires_at ? formatDate(license.expires_at) : "Never"}
          </p>
          {license.days_remaining !== null && license.days_remaining <= 30 && (
            <p
              className={`text-[10px] ${license.days_remaining <= 7 ? "font-medium text-red-600" : "text-yellow-600"}`}
            >
              {license.days_remaining}d remaining
            </p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-2 border-t border-gray-200 px-4 py-2.5 dark:border-gray-700">
        {isValid && (
          <button
            onClick={onDeactivate}
            className="rounded border border-gray-300 px-3 py-1 text-xs text-gray-600 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-400"
          >
            Deactivate
          </button>
        )}
        {(license.status === "expired" ||
          license.status === "grace" ||
          license.status === "trial_expired") && (
          <button
            onClick={onRenew}
            className="rounded bg-blue-600 px-3 py-1 text-xs font-medium text-white hover:bg-blue-700"
          >
            Renew
          </button>
        )}
      </div>
    </div>
  );
}
