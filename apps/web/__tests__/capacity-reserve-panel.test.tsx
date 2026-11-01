import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CapacityReservePanel } from "@/components/capacity-reserve-panel";

describe("CapacityReservePanel", () => {
  it("renders", () => {
    const { container } = render(
      <CapacityReservePanel totalReserved={150} totalUtilized={90}
        utilizationPct={60} underutilized={["cache"]} wasteCount={1} />
    );
    expect(container.textContent).toContain("Capacity Reservations");
    expect(container.textContent).toContain("60% utilized");
    expect(container.textContent).toContain("1 wasted");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("90");
    expect(container.textContent).toContain("cache");
  });
});
