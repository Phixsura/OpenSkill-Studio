import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppComparisonView } from "@/components/app-comparison-view";

describe("AppComparisonView", () => {
  const columns = [{ id: "a", name: "AppA", icon: "📦" }, { id: "b", name: "AppB", icon: "🚀" }];
  const comparison = [
    { metric: "rating", label: "Rating", values: { a: 4.5, b: 4.8 }, best: "b" },
    { metric: "downloads", label: "Downloads", values: { a: 10000, b: 5000 }, best: "a" },
  ];
  it("renders comparison", () => {
    const { container } = render(<AppComparisonView columns={columns} comparison={comparison} />);
    expect(container.textContent).toContain("AppA");
    expect(container.textContent).toContain("AppB");
    expect(container.textContent).toContain("Rating");
    expect(container.textContent).toContain("🏆");
  });
});
