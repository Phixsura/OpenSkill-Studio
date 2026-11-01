import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceHealthV9Panel } from "@/components/fleet-service-health-v9-panel";
describe("FleetServiceHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceHealthV9Panel services={200} uptime={99.99} />);
    expect(container.textContent).toContain("Service Health v9");
}); });
