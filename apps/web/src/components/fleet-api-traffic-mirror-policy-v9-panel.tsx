"use client";
export function FleetApiTrafficMirrorPolicyV9Panel({ policies, mirrored }: { policies: number; mirrored: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪞 Traffic Mirror Policy v9</h3>
    <div className="text-sm">{policies} policies · {mirrored.toLocaleString()} mirrored rps</div>
  </div>);
}
