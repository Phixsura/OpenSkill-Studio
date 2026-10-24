import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerformancePage } from "@/components/performance-page";

describe("PerformancePage", () => {
  const vitals = [
    { name: "LCP", display: "1200ms", threshold: "≤2500ms", score: "good", description: "Largest Contentful Paint" },
    { name: "CLS", display: "0.050", threshold: "≤0.1", score: "good", description: "Layout Shift" },
  ];
  it("renders performance", () => {
    const { container } = render(
      <PerformancePage vitals={vitals} overall="good" overallLabel="✅ Good" />
    );
    expect(container.textContent).toContain("Performance");
    expect(container.textContent).toContain("LCP");
    expect(container.textContent).toContain("1200ms");
    expect(container.textContent).toContain("✅ Good");
  });
});
