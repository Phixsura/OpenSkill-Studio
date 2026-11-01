import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRetryStormPanel } from "@/components/fleet-retry-storm-panel";
describe("FleetRetryStormPanel", () => { it("renders", () => {
    const { container } = render(<FleetRetryStormPanel total={10} amplifying={3} maxRatio={6} storm={true} />);
    expect(container.textContent).toContain("Retry Storm");
    expect(container.textContent).toContain("Retry storm!");
}); });
