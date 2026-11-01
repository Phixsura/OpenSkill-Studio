import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCrossRegionV9Panel } from "@/components/fleet-cross-region-v9-panel";
describe("FleetCrossRegionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCrossRegionV9Panel regions={5} lag={50} />);
    expect(container.textContent).toContain("Cross-Region v9");
}); });
