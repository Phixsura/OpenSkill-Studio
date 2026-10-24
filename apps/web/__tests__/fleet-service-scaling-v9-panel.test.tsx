import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceScalingV9Panel } from "@/components/fleet-service-scaling-v9-panel";
describe("FleetServiceScalingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceScalingV9Panel services={100} replicas={500} />);
    expect(container.textContent).toContain("Service Scaling v9");
}); });
