import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAdaptConcPanel } from "@/components/fleet-adapt-conc-panel";
describe("FleetAdaptConcPanel", () => { it("renders", () => {
    const { container } = render(<FleetAdaptConcPanel services={10} avgLimit={150} recentlyAdjusted={3} stable={false} />);
    expect(container.textContent).toContain("Adaptive Concurrency");
    expect(container.textContent).toContain("3 recently adjusted");
}); });
