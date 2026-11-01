import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiPerformanceV9Panel } from "@/components/fleet-api-performance-v9-panel";
describe("FleetApiPerformanceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiPerformanceV9Panel endpoints={200} avgMs={25} />);
    expect(container.textContent).toContain("API Performance v9");
}); });
