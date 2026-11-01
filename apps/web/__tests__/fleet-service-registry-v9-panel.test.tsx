import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceRegistryV9Panel } from "@/components/fleet-service-registry-v9-panel";
describe("FleetServiceRegistryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceRegistryV9Panel services={200} instances={600} />);
    expect(container.textContent).toContain("Service Registry v9");
}); });
