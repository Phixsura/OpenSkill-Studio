import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryBreadcrumb } from "@/components/category-breadcrumb";

describe("CategoryBreadcrumb", () => {
  it("renders crumbs", () => {
    const { container } = render(
      <CategoryBreadcrumb crumbs={[{ key: "connector", label: "Connectors" }, { key: "slack", label: "Slack" }]} />
    );
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("Connectors");
    expect(container.textContent).toContain("Slack");
  });
  it("last crumb not a link", () => {
    const { container } = render(
      <CategoryBreadcrumb crumbs={[{ key: "analytics", label: "Analytics" }]} />
    );
    const links = container.querySelectorAll("a");
    expect(Array.from(links).every(l => l.textContent !== "Analytics")).toBe(true);
  });
});
