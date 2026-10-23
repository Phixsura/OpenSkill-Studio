import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResponsiveCardGrid } from "@/components/responsive-card-grid";

describe("ResponsiveCardGrid", () => {
  it("renders children", () => {
    const { container } = render(
      <ResponsiveCardGrid gridClass="grid grid-cols-3 gap-4" itemsCount={2}>
        <div>Card 1</div>
        <div>Card 2</div>
      </ResponsiveCardGrid>
    );
    expect(container.textContent).toContain("Card 1");
    expect(container.textContent).toContain("Card 2");
  });
  it("shows empty state", () => {
    const { container } = render(
      <ResponsiveCardGrid gridClass="" itemsCount={0} emptyMessage="Nothing here" />
    );
    expect(container.textContent).toContain("Nothing here");
  });
});
