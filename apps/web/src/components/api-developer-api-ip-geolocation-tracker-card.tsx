"use client";

interface GeoInfo { country: string; request_count: number; unique_ip_count: number; error_count: number; }
interface Props { countries: GeoInfo[]; totalCountries: number; totalUniqueIPs: number; appName: string; }

export default function APIDeveloperAPIIPGeolocationTrackerCard({ countries, totalCountries, totalUniqueIPs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌍 IP Geolocation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right text-[10px] text-gray-400">
          <p>{totalCountries} countries</p>
          <p>{totalUniqueIPs.toLocaleString()} unique IPs</p>
        </div>
      </div>
      {countries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No geo data</p>
      ) : (
        <div className="space-y-1.5">
          {countries.map((c) => (
            <div key={c.country} className="flex items-center justify-between text-[11px]">
              <span className="font-medium text-gray-700 dark:text-gray-300">{c.country}</span>
              <div className="flex gap-2 text-gray-400">
                <span>{c.request_count.toLocaleString()} reqs</span>
                <span>{c.unique_ip_count} IPs</span>
                {c.error_count > 0 && <span className="text-red-500">{c.error_count} err</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
