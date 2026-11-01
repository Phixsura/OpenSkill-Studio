import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperStatsGrid } from "@/components/developer-stats-grid";

describe("DeveloperStatsGrid", () => {
  const cards = [
    { id: "apps", label: "Apps", value: 5, icon: "📦", change: 1 },
    { id: "revenue", label: "Revenue", value: 2500, icon: "💰", format: "currency", change: -200 },
  ];
  it("renders", () => {
    const { container } = render(<DeveloperStatsGrid cards={cards} />);
    expect(container.textContent).toContain("📦");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("↑ 1");
    expect(container.textContent).toContain("$2,500");
    expect(container.textContent).toContain("↓ 200");
  });
});
