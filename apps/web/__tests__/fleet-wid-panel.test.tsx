import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWidPanel } from "@/components/fleet-wid-panel";
describe("FleetWidPanel", () => { it("renders", () => {
    const { container } = render(<FleetWidPanel total={10} workloadIdentity={8} saKeys={2} modern={false} />);
    expect(container.textContent).toContain("Workload Identity");
    expect(container.textContent).toContain("2 still using SA keys");
}); });
