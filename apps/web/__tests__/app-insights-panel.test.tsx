import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppInsightsPanel } from "@/components/app-insights-panel";

describe("AppInsightsPanel", () => {
  it("renders insights", () => {
    const { container } = render(
      <AppInsightsPanel appId="myapp" health="excellent" kpis={[
        { label: "Installs", display: "+150" },
        { label: "API Calls", display: "500,000" },
        { label: "Error Rate", display: "0.01%" },
      ]} />
    );
    expect(container.textContent).toContain("App Insights");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("+150");
    expect(container.textContent).toContain("500,000");
    expect(container.textContent).toContain("0.01%");
  });
});
