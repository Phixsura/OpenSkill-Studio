import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIdentityMgrV9Panel } from "@/components/fleet-identity-mgr-v9-panel";
describe("FleetIdentityMgrV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetIdentityMgrV9Panel total={1000} mfa={1000} />);
    expect(container.textContent).toContain("Identity Manager v9");
}); });
