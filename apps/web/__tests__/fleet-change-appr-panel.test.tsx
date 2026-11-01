import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChangeApprPanel } from "@/components/fleet-change-appr-panel";
describe("FleetChangeApprPanel", () => { it("renders", () => {
    const { container } = render(<FleetChangeApprPanel total={10} approved={8} unapproved={2} emergency={1} compliant={false} />);
    expect(container.textContent).toContain("Change Approval");
    expect(container.textContent).toContain("2 unapproved");
}); });
