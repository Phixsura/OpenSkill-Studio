"use client";

interface TrustedDevice { device_id: string; device_name: string; fingerprint_hash: string;
  registered_at: string; trusted_until: string; }
interface TrustedDeviceListProps { devices: TrustedDevice[]; currentDeviceId: string;
  onRemove: (id: string) => void; }

const deviceIcon: Record<string, string> = {
  MacBook: "💻", iPhone: "📱", iPad: "📲", Windows: "🖥️", Chrome: "🌐",
};
const getIcon = (name: string) => {
  for (const [key, icon] of Object.entries(deviceIcon)) {
    if (name.includes(key)) return icon;
  }
  return "📱";
};

export function TrustedDeviceList({ devices, currentDeviceId, onRemove }: TrustedDeviceListProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Trusted Devices</h2>
      {devices.map(d => (
        <div key={d.device_id} className={`flex items-center justify-between rounded-lg border p-3 ${d.device_id === currentDeviceId ? "border-green-300 dark:border-green-700" : "dark:border-gray-700"}`}>
          <div className="flex items-center gap-3">
            <span className="text-xl">{getIcon(d.device_name)}</span>
            <div>
              <p className="text-sm font-medium">
                {d.device_name}
                {d.device_id === currentDeviceId && <span className="ml-1 text-xs text-green-500">(this device)</span>}
              </p>
              <p className="text-xs text-gray-400">
                Trusted until {new Date(d.trusted_until).toLocaleDateString()}
              </p>
            </div>
          </div>
          {d.device_id !== currentDeviceId && (
            <button onClick={() => onRemove(d.device_id)} className="text-xs text-red-500">Remove</button>
          )}
        </div>
      ))}
      {devices.length === 0 && <p className="text-sm text-gray-400">No trusted devices</p>}
    </div>
  );
}
