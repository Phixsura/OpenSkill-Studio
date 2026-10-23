import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComplianceDashboard } from "@/components/compliance-dashboard";

describe("ComplianceDashboard", () => {
  const checks = [
    { check: "data_encryption", pass: true, label: "Data Encryption" },
    { check: "consent_management", pass: false, label: "Consent Management" },
  ];
  it("renders compliance", () => {
    const { container } = render(
      <ComplianceDashboard framework="GDPR" region="EU" checks={checks}
        score={50} compliant={false} passed={1} failed={1} />
    );
    expect(container.textContent).toContain("GDPR");
    expect(container.textContent).toContain("EU");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Non-compliant");
    expect(container.textContent).toContain("Data Encryption");
  });
});
