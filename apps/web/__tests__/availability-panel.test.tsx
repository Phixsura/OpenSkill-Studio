import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AvailabilityPanel } from "@/components/availability-panel";
describe("AvailabilityPanel", () => {
  it("renders", () => {
    const { container } = render(
      <AvailabilityPanel compositePct={99.7} downtimeMinutes={129.6} nines={2.5}
        components={3} architecture="serial" />
    );
    expect(container.textContent).toContain("Availability");
    expect(container.textContent).toContain("99.7%");
    expect(container.textContent).toContain("2.5-nines");
    expect(container.textContent).toContain("129.6min");
    expect(container.textContent).toContain("serial");
  });
});
