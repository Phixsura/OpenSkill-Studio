import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDaprPanel } from "@/components/fleet-dapr-panel";
describe("FleetDaprPanel", () => { it("renders", () => {
    const { container } = render(<FleetDaprPanel total={10} healthy={9} components={40} allHealthy={false} />);
    expect(container.textContent).toContain("Dapr");
    expect(container.textContent).toContain("Unhealthy");
}); });
