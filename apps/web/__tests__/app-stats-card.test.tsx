import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppStatsCard } from "@/components/app-stats-card";

describe("AppStatsCard", () => {
  const metrics = [
    { label: "Installs", display: "25K", icon: "📥" },
    { label: "Rating", display: "4.5", icon: "⭐" },
  ];
  it("renders stats card", () => {
    const { container } = render(
      <AppStatsCard name="MyApp" icon="🚀" metrics={metrics} health="good" />
    );
    expect(container.textContent).toContain("MyApp");
    expect(container.textContent).toContain("25K");
    expect(container.textContent).toContain("4.5");
    expect(container.textContent).toContain("Installs");
  });
});
