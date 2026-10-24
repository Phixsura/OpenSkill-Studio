import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApikeyMgmtPanel } from "@/components/fleet-apikey-mgmt-panel";
describe("FleetApikeyMgmtPanel", () => { it("renders", () => {
    const { container } = render(<FleetApikeyMgmtPanel total={50} active={45} expired={3} expiringSoon={2} needsRotation={true} />);
    expect(container.textContent).toContain("API Keys");
    expect(container.textContent).toContain("2 expiring");
}); });
