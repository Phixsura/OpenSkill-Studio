import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComparisonTableV2 } from "@/components/comparison-table-v2";

describe("ComparisonTableV2", () => {
  it("renders comparison", () => {
    const apps = [{ id: "a1", name: "App A" }, { id: "a2", name: "App B" }];
    const rows = [{ dimension: "Rating", icon: "⭐", values: { a1: 4.5, a2: 4.0 }, winner: "a1" }];
    const { container } = render(<ComparisonTableV2 apps={apps} rows={rows} />);
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("App B");
    expect(container.textContent).toContain("4.5");
    expect(container.textContent).toContain("🏆");
  });
});
