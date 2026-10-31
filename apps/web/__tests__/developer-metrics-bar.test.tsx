import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperMetricsBar } from "@/components/developer-metrics-bar";

describe("DeveloperMetricsBar", () => {
  it("renders", () => {
    const metrics = [
      { key: "installs", label: "Installs", value: 5000, icon: "📥", format: "number" },
      { key: "revenue", label: "Revenue", value: 9900, icon: "💰", format: "currency" },
      { key: "rating", label: "Rating", value: 4.5, icon: "⭐", format: "rating" },
    ];
    const { container } = render(<DeveloperMetricsBar metrics={metrics} period="30d" />);
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("$99.00");
    expect(container.textContent).toContain("4.5 ★");
    expect(container.textContent).toContain("30d");
  });
});
