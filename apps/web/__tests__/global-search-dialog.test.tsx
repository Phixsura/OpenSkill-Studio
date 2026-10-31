import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GlobalSearchDialog } from "@/components/global-search-dialog";

describe("GlobalSearchDialog", () => {
  const sections = {
    Apps: [{ type: "app", title: "Code Editor", subtitle: "Edit code", icon: "📦", href: "/apps/a1" }],
  };
  it("renders search dialog", () => {
    const { container } = render(
      <GlobalSearchDialog sections={sections} total={1} onSearch={vi.fn()} onSelect={vi.fn()} onClose={vi.fn()} />
    );
    expect(container.textContent).toContain("Code Editor");
    expect(container.textContent).toContain("Apps");
    expect(container.querySelector("input")).toBeTruthy();
  });
});
