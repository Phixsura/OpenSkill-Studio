import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ResourceTagEditor } from "@/components/resource-tag-editor";

describe("ResourceTagEditor", () => {
  const tags = { env: "prod", team: "api" };
  it("renders", () => {
    const { container } = render(<ResourceTagEditor tags={tags} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("Tags");
    expect(container.textContent).toContain("env");
    expect(container.textContent).toContain("prod");
    expect(container.textContent).toContain("team");
  });
  it("remove", () => {
    const fn = vi.fn();
    const { container } = render(<ResourceTagEditor tags={tags} onAdd={vi.fn()} onRemove={fn} />);
    const removeBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "×");
    fireEvent.click(removeBtns[0]);
    expect(fn).toHaveBeenCalledWith("env");
  });
});
