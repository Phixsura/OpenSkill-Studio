import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppInsightsPanel } from "@/components/app-insights-panel";

describe("AppInsightsPanel", () => {
  it("renders insights", () => {
    const insights = [
      { type: "positive", icon: "📈", title: "Install Growth", message: "Up 50%!" },
      { type: "warning", icon: "⭐", title: "Low Ratings", message: "Check reviews" },
    ];
    const { container } = render(<AppInsightsPanel insights={insights} />);
    expect(container.textContent).toContain("Install Growth");
    expect(container.textContent).toContain("Up 50%!");
    expect(container.textContent).toContain("Low Ratings");
  });
  it("empty", () => {
    const { container } = render(<AppInsightsPanel insights={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
