import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSliPanel } from "@/components/fleet-sli-panel";
describe("FleetSliPanel", () => { it("renders", () => {
    const { container } = render(<FleetSliPanel total={10} meetingTarget={8} missingTarget={2} compliancePct={80} />);
    expect(container.textContent).toContain("Fleet SLIs");
    expect(container.textContent).toContain("80% compliant");
}); });
