import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryPageHeader } from "@/components/category-page-header";

describe("CategoryPageHeader", () => {
  it("shows category", () => {
    const { container } = render(<CategoryPageHeader category="connector" description="Connect systems" totalApps={42} />);
    expect(container.textContent).toContain("connector");
    expect(container.textContent).toContain("42 apps");
  });
  it("shows icon", () => {
    const { container } = render(<CategoryPageHeader category="automation" description="Auto" totalApps={0} />);
    expect(container.textContent).toContain("🤖");
  });
});
