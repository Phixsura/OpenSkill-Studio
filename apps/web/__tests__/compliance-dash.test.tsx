import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComplianceDash } from "@/components/compliance-dash";

describe("ComplianceDash", () => {
  it("renders", () => {
    const { container } = render(
      <ComplianceDash score={66.7} compliant={2} nonCompliant={1}
        violations={[
          { policy: "encryption_required", field: "encryption", severity: "critical" },
        ]} />
    );
    expect(container.textContent).toContain("Compliance");
    expect(container.textContent).toContain("66.7% score");
    expect(container.textContent).toContain("2");
    expect(container.textContent).toContain("1");
    expect(container.textContent).toContain("encryption_required");
    expect(container.textContent).toContain("critical");
  });
});
