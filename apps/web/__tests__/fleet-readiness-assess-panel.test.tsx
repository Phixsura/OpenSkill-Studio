import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReadinessAssessPanel } from "@/components/fleet-readiness-assess-panel";
describe("FleetReadinessAssessPanel", () => { it("renders", () => {
    const { container } = render(<FleetReadinessAssessPanel totalChecks={50} passed={48} blockers={0} score={96} launchReady={true} />);
    expect(container.textContent).toContain("Launch Readiness");
    expect(container.textContent).toContain("READY");
}); });
