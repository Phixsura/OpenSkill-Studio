import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppComparisonSideBySide } from "@/components/app-comparison-side-by-side";

describe("AppComparisonSideBySide", () => {
  const apps = [{ id: "a1", name: "App A" }, { id: "a2", name: "App B" }];
  const rows = [{ criterion: "rating", a1: 4.5, a2: 4.8 },
                { criterion: "has_api", a1: true, a2: false }];
  it("renders", () => {
    const { container } = render(
      <AppComparisonSideBySide apps={apps} rows={rows} scores={{ a1: 14.5, a2: 4.8 }} winner="a1" />
    );
    expect(container.textContent).toContain("Compare Apps");
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("🏆");
    expect(container.textContent).toContain("4.5");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("❌");
    expect(container.textContent).toContain("14.5");
  });
});
