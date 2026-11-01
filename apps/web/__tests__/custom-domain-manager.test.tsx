import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CustomDomainManager } from "@/components/custom-domain-manager";

describe("CustomDomainManager", () => {
  it("renders domains", () => {
    const { container } = render(
      <CustomDomainManager onAdd={vi.fn()} onVerify={vi.fn()} onRemove={vi.fn()}
        domains={[
          { domain: "app.example.com", verified: true, ssl: true, dnsRecord: "CNAME app.example.com -> apps.openskill.io" },
          { domain: "beta.test.com", verified: false, ssl: false, dnsRecord: "CNAME beta.test.com -> apps.openskill.io" },
        ]} />
    );
    expect(container.textContent).toContain("Custom Domains");
    expect(container.textContent).toContain("app.example.com");
    expect(container.textContent).toContain("Verified");
    expect(container.textContent).toContain("SSL");
    expect(container.textContent).toContain("beta.test.com");
    expect(container.textContent).toContain("Verify");
  });
});
