import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppStatsCardGrid } from "@/components/app-stats-card-grid";

describe("AppStatsCardGrid", () => {
  it("renders metrics", () => {
    const { container } = render(<AppStatsCardGrid metrics={[{ label: "Installs", value: 42, icon: "📥" }]} />);
    expect(container.textContent).toContain("42");
    expect(container.textContent).toContain("Installs");
  });
});
