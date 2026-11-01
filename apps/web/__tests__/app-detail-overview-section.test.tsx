import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppDetailOverviewSection } from "@/components/app-detail-overview-section";

describe("AppDetailOverviewSection", () => {
  it("shows all info", () => {
    const { container } = render(<AppDetailOverviewSection description="Great app" category="connector" developerName="Dev" verified={true} installCount={100} healthScore={95} createdAt="Jan 2026" />);
    expect(container.textContent).toContain("Great app");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("Dev");
  });
  it("handles null description", () => {
    const { container } = render(<AppDetailOverviewSection description={null} category="automation" developerName="X" verified={false} installCount={0} healthScore={100} createdAt="" />);
    expect(container).toBeTruthy();
  });
});
