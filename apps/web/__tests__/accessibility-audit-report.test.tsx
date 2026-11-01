import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AccessibilityAuditReport } from "@/components/accessibility-audit-report";

describe("AccessibilityAuditReport", () => {
  const findings = [
    { id: "alt-text", level: "A", description: "Images have alt text", passed: true },
    { id: "color-contrast", level: "AA", description: "Color contrast", passed: false },
  ];
  it("renders", () => {
    const { container } = render(
      <AccessibilityAuditReport findings={findings} score={50} grade="C"
        wcagACompliant={true} wcagAACompliant={false} />
    );
    expect(container.textContent).toContain("Accessibility Audit");
    expect(container.textContent).toContain("C");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("✗");
    expect(container.textContent).toContain("Images have alt text");
  });
});
