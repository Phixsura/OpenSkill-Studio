import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TosComplianceCard } from "@/components/tos-compliance-card";

describe("TosComplianceCard", () => {
  it("renders compliance", () => {
    const { container } = render(
      <TosComplianceCard compliant={false} score={60} results={[
        { title: "Data Privacy", description: "", passed: true, required: true, critical: false },
        { title: "No Malware", description: "", passed: false, required: true, critical: true },
      ]} />
    );
    expect(container.textContent).toContain("TOS Compliance");
    expect(container.textContent).toContain("Non-compliant");
    expect(container.textContent).toContain("60%");
    expect(container.textContent).toContain("Data Privacy");
    expect(container.textContent).toContain("No Malware");
  });
});
