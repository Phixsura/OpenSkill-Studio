"use client";
export function FleetFeatureAdoptionV9Panel({ features, adoption }: { features: number; adoption: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Feature Adoption v9</h3>
    <div className="text-sm">{features} features · {adoption}% avg adoption</div>
  </div>);
}
