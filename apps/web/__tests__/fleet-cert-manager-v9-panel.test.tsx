import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCertManagerV9Panel } from "@/components/fleet-cert-manager-v9-panel";
describe("FleetCertManagerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCertManagerV9Panel total={500} expiring={0} />);
    expect(container.textContent).toContain("Cert Manager v9");
}); });
