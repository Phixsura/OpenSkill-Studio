import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiServiceRegistryV9Panel } from "@/components/fleet-api-service-registry-v9-panel";
describe("FleetApiServiceRegistryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiServiceRegistryV9Panel services={200} healthy={200} />);
    expect(container.textContent).toContain("API Service Registry v9");
}); });
