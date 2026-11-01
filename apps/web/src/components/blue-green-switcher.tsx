"use client";

interface BlueGreenSwitcherProps { service: string; activeSlot: string;
  blueVersion: string; greenVersion: string; blueTraffic: number;
  greenTraffic: number; onSwitch: (slot: string) => void; }

export function BlueGreenSwitcher({ service, activeSlot, blueVersion, greenVersion, blueTraffic, greenTraffic, onSwitch }: BlueGreenSwitcherProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">🔵🟢 Blue-Green: {service}</h3>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700">
        {[{ slot: "blue", version: blueVersion, traffic: blueTraffic, color: "blue" },
          { slot: "green", version: greenVersion, traffic: greenTraffic, color: "green" }].map(s => (
          <div key={s.slot} className={`p-4 text-center ${s.slot === activeSlot ? `bg-${s.color}-50 dark:bg-${s.color}-900/10` : ""}`}>
            <div className={`text-2xl mb-1 ${s.color === "blue" ? "text-blue-500" : "text-green-500"}`}>
              {s.slot === activeSlot ? "●" : "○"}
            </div>
            <div className="text-sm font-bold capitalize">{s.slot}</div>
            <div className="text-xs text-gray-400">v{s.version}</div>
            <div className="text-xs font-bold mt-1">{s.traffic}% traffic</div>
            {s.slot !== activeSlot && (
              <button onClick={() => onSwitch(s.slot)}
                className="mt-2 px-3 py-1 text-xs bg-blue-500 text-white rounded">Switch</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
