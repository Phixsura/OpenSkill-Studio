import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSslCertMonitorV9Panel } from "@/components/fleet-ssl-cert-monitor-v9-panel";
describe("FleetSslCertMonitorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSslCertMonitorV9Panel certs={200} expiring={0} />);
    expect(container.textContent).toContain("SSL Cert Monitor v9");
}); });
