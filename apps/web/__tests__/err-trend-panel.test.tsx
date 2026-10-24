import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrTrendPanel } from "@/components/err-trend-panel";
describe("ErrTrendPanel", () => {
  it("renders", () => {
    const { container } = render(<ErrTrendPanel trend="worsening" change={2.35} recentRate={2.5} olderRate={0.15} />);
    expect(container.textContent).toContain("Error Trend");
    expect(container.textContent).toContain("worsening");
    expect(container.textContent).toContain("+2.35%");
    expect(container.textContent).toContain("2.5%");
  });
});
