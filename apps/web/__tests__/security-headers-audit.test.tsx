import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecurityHeadersAudit } from "@/components/security-headers-audit";

describe("SecurityHeadersAudit", () => {
  it("perfect", () => {
    const { container } = render(
      <SecurityHeadersAudit findings={[]} score={100} grade="A" present={6} totalRecommended={6} />
    );
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("6/6");
    expect(container.textContent).toContain("All recommended");
  });
  it("findings", () => {
    const findings = [{ header: "X-Frame-Options", status: "missing", severity: "high",
      recommendation: "Add: DENY" }];
    const { container } = render(
      <SecurityHeadersAudit findings={findings} score={83} grade="B" present={5} totalRecommended={6} />
    );
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("X-Frame-Options");
    expect(container.textContent).toContain("❌");
  });
});
