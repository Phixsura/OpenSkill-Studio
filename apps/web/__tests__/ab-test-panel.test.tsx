import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AbTestPanel } from "@/components/ab-test-panel";

describe("AbTestPanel", () => {
  const results = [
    { id: "A", name: "Control", impressions: 1000, conversions: 50, conversion_rate: 5.0 },
    { id: "B", name: "Test", impressions: 1000, conversions: 75, conversion_rate: 7.5 },
  ];
  it("renders results with winner", () => {
    const { container } = render(<AbTestPanel results={results} winner="B" totalImpressions={2000} />);
    expect(container.textContent).toContain("Control");
    expect(container.textContent).toContain("Test");
    expect(container.textContent).toContain("7.5%");
    expect(container.textContent).toContain("Winner");
    expect(container.textContent).toContain("2,000");
  });
});
