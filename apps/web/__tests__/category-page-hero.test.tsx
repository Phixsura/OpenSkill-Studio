import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CategoryPageHero } from "@/components/category-page-hero";

describe("CategoryPageHero", () => {
  it("renders hero", () => {
    const subs = [{ id: "crm", name: "CRM" }, { id: "chat", name: "Chat" }];
    const { container } = render(
      <CategoryPageHero name="Connectors" icon="🔗" description="Integration tools"
        appCount={150} subcategories={subs} onSubcategoryClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Connectors");
    expect(container.textContent).toContain("Integration tools");
    expect(container.textContent).toContain("150 apps");
    expect(container.textContent).toContain("CRM");
  });
  it("subcategory click", () => {
    const fn = vi.fn();
    const { container } = render(
      <CategoryPageHero name="X" icon="" description="" appCount={0}
        subcategories={[{ id: "crm", name: "CRM" }]} onSubcategoryClick={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("crm");
  });
});
