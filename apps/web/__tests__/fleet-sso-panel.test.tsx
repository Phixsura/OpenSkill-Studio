import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSsoPanel } from "@/components/fleet-sso-panel";
describe("FleetSsoPanel", () => { it("renders", () => {
    const { container } = render(<FleetSsoPanel total={3} healthy={1} degraded={1} down={1} allOk={false} />);
    expect(container.textContent).toContain("SSO Providers");
    expect(container.textContent).toContain("SSO issues");
}); });
