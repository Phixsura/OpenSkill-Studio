import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConsulPanel } from "@/components/fleet-consul-panel";
describe("FleetConsulPanel", () => { it("renders", () => {
    const { container } = render(<FleetConsulPanel datacenters={3} healthy={3} services={200} kvKeys={10000} />);
    expect(container.textContent).toContain("Consul");
    expect(container.textContent).toContain("10,000 KV");
}); });
