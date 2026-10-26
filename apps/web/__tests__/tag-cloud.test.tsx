import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TagCloud } from "@/components/tag-cloud";
const tags = [{ tag: "api", count: 50 }, { tag: "ui", count: 30 }];
describe("TagCloud", () => {
  it("renders tags", () => {
    const { container } = render(<TagCloud tags={tags} />);
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("50");
  });
  it("calls onSelect", () => {
    const fn = vi.fn();
    const { getByText } = render(<TagCloud tags={tags} onSelect={fn} />);
    fireEvent.click(getByText("api 50"));
    expect(fn).toHaveBeenCalledWith("api");
  });
});
