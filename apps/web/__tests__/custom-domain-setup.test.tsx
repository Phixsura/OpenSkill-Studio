import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CustomDomainSetup } from "@/components/custom-domain-setup";

describe("CustomDomainSetup", () => {
  it("renders pending domain", () => {
    const { container } = render(
      <CustomDomainSetup domain="app.example.com" status="pending_verification"
        verified={false} verificationToken="openskill-verify-app-example-com"
        dnsRecords={[
          { type: "CNAME", name: "app.example.com", value: "app.openskill.io", ttl: 3600 },
        ]} />
    );
    expect(container.textContent).toContain("Custom Domain");
    expect(container.textContent).toContain("app.example.com");
    expect(container.textContent).toContain("CNAME");
    expect(container.textContent).toContain("Verification Required");
    expect(container.textContent).toContain("openskill-verify-app-example-com");
  });
});
