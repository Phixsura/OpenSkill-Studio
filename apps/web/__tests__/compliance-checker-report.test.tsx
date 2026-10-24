import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComplianceCheckerReport } from "@/components/compliance-checker-report";

describe("ComplianceCheckerReport", () => {
  const results = [
    { id: "gdpr_privacy", label: "Privacy policy", required: true, met: true, status: "pass" },
    { id: "gdpr_consent", label: "Cookie consent", required: true, met: false, status: "fail" },
  ];
  it("renders", () => {
    const { container } = render(
      <ComplianceCheckerReport framework="GDPR" compliant={false} results={results} score={50} />
    );
    expect(container.textContent).toContain("GDPR Compliance");
    expect(container.textContent).toContain("Non-Compliant");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("❌");
  });
});
