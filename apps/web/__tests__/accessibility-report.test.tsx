import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AccessibilityReport } from "@/components/accessibility-report";

describe("AccessibilityReport", () => {
  const results = [
    { id: "alt_text", description: "Images must have alt text", wcag: "1.1.1", level: "A", pass: true, details: "" },
    { id: "color_contrast", description: "Text must have sufficient contrast", wcag: "1.4.3", level: "AA", pass: false, details: "Ratio 3.5:1" },
  ];
  it("renders audit results", () => {
    const { container } = render(
      <AccessibilityReport results={results} score={50} grade="C" passed={1} failed={1} />
    );
    expect(container.textContent).toContain("Accessibility Audit");
    expect(container.textContent).toContain("C");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("1 passed");
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("WCAG 1.4.3");
  });
});
