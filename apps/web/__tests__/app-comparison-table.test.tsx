import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppComparisonTable } from "@/components/app-comparison-table";

describe("AppComparisonTable", () => {
  it("renders feature matrix", () => {
    const { container } = render(
      <AppComparisonTable
        apps={[{ id: "a1", name: "App A" }, { id: "a2", name: "App B" }]}
        matrix={[{ feature: "Auth", a1: true, a2: false }, { feature: "Webhooks", a1: true, a2: true }]}
      />
    );
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("Auth");
    expect(container.querySelectorAll("tr").length).toBe(3); // header + 2 rows
  });
  it("shows message for less than 2 apps", () => {
    const { container } = render(<AppComparisonTable apps={[{ id: "a1", name: "Solo" }]} matrix={[]} />);
    expect(container.textContent).toContain("at least 2 apps");
  });
});
