import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResponsiveGrid } from "@/components/responsive-grid";

describe("ResponsiveGrid", () => {
  it("renders children", () => {
    const { container } = render(
      <ResponsiveGrid><div>Item 1</div><div>Item 2</div></ResponsiveGrid>
    );
    expect(container.textContent).toContain("Item 1");
    expect(container.textContent).toContain("Item 2");
    expect(container.querySelector("[class*='grid']")).toBeTruthy();
  });
});
