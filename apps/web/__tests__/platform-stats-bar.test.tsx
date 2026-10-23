import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformStatsBar } from "@/components/platform-stats-bar";

describe("PlatformStatsBar", () => {
  const stats = [
    { label: "Apps", display: "1.5K", icon: "📦" },
    { label: "Downloads", display: "2.5M", icon: "📥" },
  ];
  it("renders stats", () => {
    const { container } = render(<PlatformStatsBar stats={stats} />);
    expect(container.textContent).toContain("1.5K");
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("2.5M");
    expect(container.textContent).toContain("📦");
  });
});
