import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEngagementPanel } from "@/components/fleet-engagement-panel";
describe("FleetEngagementPanel", () => { it("renders", () => {
    const { container } = render(<FleetEngagementPanel dau={500} mau={2000} stickinessPct={25} avgSessionMin={15} engaged={true} />);
    expect(container.textContent).toContain("Engagement");
    expect(container.textContent).toContain("25% sticky");
}); });
