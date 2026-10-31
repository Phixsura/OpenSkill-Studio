import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiGlobalHealthV9Panel } from "@/components/fleet-api-global-health-v9-panel";
describe("FleetApiGlobalHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiGlobalHealthV9Panel />);
    expect(container.textContent).toContain("ALL APIS HEALTHY");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
