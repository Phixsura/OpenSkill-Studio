import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiConformanceV9Panel } from "@/components/fleet-api-conformance-v9-panel";
describe("FleetApiConformanceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiConformanceV9Panel tests={100} violations={0} />);
    expect(container.textContent).toContain("API Conformance v9");
}); });
