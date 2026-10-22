import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryIcon } from "@/components/category-icon";

const CATEGORIES = ["connector", "automation", "analytics", "ui_extension", "ecosystem_source", "content_pack", "workflow_adapter"];

describe("CategoryIcon", () => {
  it.each(CATEGORIES)("renders %s category", (category) => {
    const { container } = render(<CategoryIcon category={category} />);
    expect(container.firstChild).toBeTruthy();
  });

  it("renders unknown category", () => {
    const { container } = render(<CategoryIcon category="unknown" />);
    expect(container.firstChild).toBeTruthy();
  });
});
