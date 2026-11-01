import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ComplianceCheckerCard from "../src/components/api-developer-platform-sdk-consumer-api-compliance-checker-card";

describe("ComplianceCheckerCard", () => {
  it("renders title and frameworks", () => {
    const { container } = render(<ComplianceCheckerCard />);
    expect(container.textContent).toContain("Compliance Checker");
    expect(container.textContent).toContain("GDPR");
    expect(container.textContent).toContain("SOC2");
    expect(container.textContent).toContain("PCI DSS");
  });

  it("shows scores and compliant count", () => {
    const { container } = render(<ComplianceCheckerCard />);
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("87.5%");
    expect(container.textContent).toContain("1/3 frameworks fully compliant");
  });
});
