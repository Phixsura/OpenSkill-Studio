import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHealthCheckV9Panel } from "@/components/fleet-health-check-v9-panel";
describe("FleetHealthCheckV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetHealthCheckV9Panel endpoints={200} up={200} />);
    expect(container.textContent).toContain("Health Check v9");
}); });
