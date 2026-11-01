import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOwnershipPanel } from "@/components/fleet-ownership-panel";
describe("FleetOwnershipPanel", () => { it("renders", () => {
    const { container } = render(<FleetOwnershipPanel total={100} owned={85} unowned={15} coveragePct={85} />);
    expect(container.textContent).toContain("Code Ownership");
    expect(container.textContent).toContain("15 unowned");
}); });
