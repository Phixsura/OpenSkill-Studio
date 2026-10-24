import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceReliabilityV9Panel } from "@/components/fleet-service-reliability-v9-panel";
describe("FleetServiceReliabilityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceReliabilityV9Panel services={200} reliability={99.99} />);
    expect(container.textContent).toContain("Service Reliability v9");
}); });
