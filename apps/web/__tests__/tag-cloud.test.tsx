import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TagCloud } from "@/components/tag-cloud";

describe("TagCloud", () => {
  const tags = [
    { tag: "auth", count: 15, weight: 100, size: 36 },
    { tag: "api", count: 10, weight: 67, size: 24 },
    { tag: "security", count: 5, weight: 33, size: 12 },
  ];
  it("renders", () => {
    const { container } = render(<TagCloud tags={tags} onTagClick={vi.fn()} />);
    expect(container.textContent).toContain("Popular Tags");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("(15)");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("security");
  });
  it("click tag", () => {
    const fn = vi.fn();
    const { container } = render(<TagCloud tags={tags} onTagClick={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("auth");
  });
});
