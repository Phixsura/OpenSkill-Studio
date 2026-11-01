import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QuickStatsBar } from "@/components/quick-stats-bar";

describe("QuickStatsBar", () => {
  it("renders stats", () => {
    const { container } = render(
      <QuickStatsBar stats={[
        { label: "Apps", display: "250", icon: "📱" },
        { label: "Developers", display: "1,500", icon: "👩‍💻" },
        { label: "Uptime", display: "99.95%", icon: "🟢" },
      ]} />
    );
    expect(container.textContent).toContain("250");
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("99.95%");
  });
});
