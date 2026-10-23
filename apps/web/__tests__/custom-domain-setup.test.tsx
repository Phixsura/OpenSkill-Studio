import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CustomDomainSetup } from "@/components/custom-domain-setup";

describe("CustomDomainSetup", () => {
  it("renders setup form", () => {
    const { container } = render(
      <CustomDomainSetup domain={null} status={null} dnsRecords={[]} ssl={null}
        statusIcon="" statusMessage="" onSetup={vi.fn()} onVerify={vi.fn()} />
    );
    expect(container.textContent).toContain("Custom Domain");
    expect(container.textContent).toContain("Setup");
  });
  it("renders pending verification", () => {
    const dns = [{ type: "CNAME", name: "app.example.com", value: "x.apps.openskill.dev" }];
    const { container } = render(
      <CustomDomainSetup domain="app.example.com" status="pending_verification"
        dnsRecords={dns} ssl={{ status: "pending", issuer: "Let's Encrypt", autoRenew: true }}
        statusIcon="🔴" statusMessage="Waiting for DNS" onSetup={vi.fn()} onVerify={vi.fn()} />
    );
    expect(container.textContent).toContain("app.example.com");
    expect(container.textContent).toContain("CNAME");
    expect(container.textContent).toContain("Verify DNS");
  });
});
