import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSvcMapPanel } from "@/components/fleet-svc-map-panel";
describe("FleetSvcMapPanel", () => { it("renders", () => {
    const { container } = render(<FleetSvcMapPanel services={20} internal={15} external={5} connections={50} avgConn={2.5} />);
    expect(container.textContent).toContain("Service Map");
    expect(container.textContent).toContain("50 connections");
}); });
