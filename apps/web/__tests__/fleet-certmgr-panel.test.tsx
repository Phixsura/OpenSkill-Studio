import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCertmgrPanel } from "@/components/fleet-certmgr-panel";
describe("FleetCertmgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetCertmgrPanel total={20} ready={18} expiring={2} failedRenewal={1} healthy={false} />);
    expect(container.textContent).toContain("cert-manager");
    expect(container.textContent).toContain("2 expiring");
}); });
