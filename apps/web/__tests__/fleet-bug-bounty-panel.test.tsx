import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBugBountyPanel } from "@/components/fleet-bug-bounty-panel";
describe("FleetBugBountyPanel", () => { it("renders", () => {
    const { container } = render(<FleetBugBountyPanel totalReports={50} valid={30} totalPaid={25000} critical={3} />);
    expect(container.textContent).toContain("Bug Bounty");
    expect(container.textContent).toContain("$25,000");
}); });
