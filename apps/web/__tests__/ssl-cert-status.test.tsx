import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SslCertStatus } from "@/components/ssl-cert-status";

describe("SslCertStatus", () => {
  it("renders certs", () => {
    const { container } = render(
      <SslCertStatus overall="critical" valid={1} expiringSoon={1} expired={1}
        certs={[
          { domain: "old.example.com", issuer: "DigiCert", daysUntilExpiry: -5, status: "expired", autoRenew: false },
          { domain: "app.example.com", issuer: "LE", daysUntilExpiry: 15, status: "expiring", autoRenew: true },
        ]} />
    );
    expect(container.textContent).toContain("SSL Certificates");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("old.example.com");
    expect(container.textContent).toContain("expired");
    expect(container.textContent).toContain("1 valid");
    expect(container.textContent).toContain("1 expiring");
  });
});
