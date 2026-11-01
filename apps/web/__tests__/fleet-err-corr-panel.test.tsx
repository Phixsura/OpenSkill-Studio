import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetErrCorrPanel } from "@/components/fleet-err-corr-panel";
describe("FleetErrCorrPanel", () => { it("renders", () => {
    const { container } = render(<FleetErrCorrPanel totalErrors={50} servicesAffected={5} hotspot="auth-svc" cascading={true} />);
    expect(container.textContent).toContain("Error Correlation");
    expect(container.textContent).toContain("Cascading failure");
}); });
