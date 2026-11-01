import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTlsExpiryPanel } from "@/components/fleet-tls-expiry-panel";
describe("FleetTlsExpiryPanel", () => { it("renders", () => {
    const { container } = render(<FleetTlsExpiryPanel total={10} expiringSoon={2} expired={1} allValid={false} />);
    expect(container.textContent).toContain("Fleet TLS Certs");
    expect(container.textContent).toContain("1 expired");
}); });
