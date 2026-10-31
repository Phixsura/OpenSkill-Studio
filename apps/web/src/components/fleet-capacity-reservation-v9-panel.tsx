"use client";
export function FleetCapacityReservationV9Panel({ reservations, savings }: { reservations: number; savings: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Capacity Reservation v9</h3>
    <div className="text-sm">{reservations} reservations · ${savings.toLocaleString()}/mo saved</div>
  </div>);
}
