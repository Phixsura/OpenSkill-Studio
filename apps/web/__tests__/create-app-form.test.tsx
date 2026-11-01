import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CreateAppForm } from "@/components/create-app-form";

describe("CreateAppForm", () => {
  it("renders form", () => {
    const { container } = render(
      <CreateAppForm categories={["tools", "productivity"]} onSubmit={vi.fn()} />
    );
    expect(container.textContent).toContain("Create New App");
    expect(container.textContent).toContain("App Name");
    expect(container.textContent).toContain("Slug");
    expect(container.textContent).toContain("Description");
    expect(container.textContent).toContain("Category");
    expect(container.textContent).toContain("Create App");
  });
});
