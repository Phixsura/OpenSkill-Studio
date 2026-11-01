import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMockSrvPanel } from "@/components/fleet-mock-srv-panel";
describe("FleetMockSrvPanel", () => { it("renders", () => {
    const { container } = render(<FleetMockSrvPanel total={10} active={8} hits={5000} wellUsed={true} />);
    expect(container.textContent).toContain("Mock Server");
    expect(container.textContent).toContain("Well-utilized");
}); });
