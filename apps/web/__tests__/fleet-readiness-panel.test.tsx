import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReadinessPanel } from "@/components/fleet-readiness-panel";
describe("FleetReadinessPanel", () => { it("renders", () => {
    const { container } = render(<FleetReadinessPanel ready={2} notReady={1} allReady={false} />);
    expect(container.textContent).toContain("Fleet Readiness");
    expect(container.textContent).toContain("1 not ready");
}); });
