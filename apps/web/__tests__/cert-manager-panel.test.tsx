import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CertManagerPanel } from "@/components/cert-manager-panel";

describe("CertManagerPanel", () => {
  it("renders certs", () => {
    const { container } = render(
      <CertManagerPanel needsAction={true} onRenew={vi.fn()} certs={[
        { domain: "app.com", daysLeft: 60, status: "valid", needsRenewal: false },
        { domain: "old.com", daysLeft: 5, status: "expiring_soon", needsRenewal: true },
      ]} />
    );
    expect(container.textContent).toContain("TLS Certificates");
    expect(container.textContent).toContain("Action Required");
    expect(container.textContent).toContain("app.com");
    expect(container.textContent).toContain("60d left");
    expect(container.textContent).toContain("old.com");
    expect(container.textContent).toContain("Renew");
  });
});
