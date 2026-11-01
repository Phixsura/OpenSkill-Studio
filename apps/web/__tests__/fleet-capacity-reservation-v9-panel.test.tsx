import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCapacityReservationV9Panel } from "@/components/fleet-capacity-reservation-v9-panel";
describe("FleetCapacityReservationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCapacityReservationV9Panel reservations={20} savings={50000} />);
    expect(container.textContent).toContain("Capacity Reservation v9");
}); });
