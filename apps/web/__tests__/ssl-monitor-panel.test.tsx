import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SslMonitorPanel } from "@/components/ssl-monitor-panel";

describe("SslMonitorPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SslMonitorPanel valid={1} expiringSoon={1} expired={1} critical={true}
        certs={[
          { domain: "api.example.com", issuer: "letsencrypt", daysUntilExpiry: 90 },
          { domain: "web.example.com", issuer: "letsencrypt", daysUntilExpiry: 15 },
          { domain: "old.example.com", issuer: "letsencrypt", daysUntilExpiry: -5 },
        ]} />
    );
    expect(container.textContent).toContain("SSL Certificates");
    expect(container.textContent).toContain("1 expired");
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("90d left");
    expect(container.textContent).toContain("EXPIRED");
  });
});
