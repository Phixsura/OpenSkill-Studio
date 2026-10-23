import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TagCloud } from "@/components/tag-cloud";

describe("TagCloud", () => {
  const tags = [{ tag: "webhook", count: 50 }, { tag: "api", count: 30 }, { tag: "oauth", count: 10 }];
  it("renders tags", () => {
    const { container } = render(<TagCloud tags={tags} onTagClick={vi.fn()} />);
    expect(container.textContent).toContain("webhook");
    expect(container.textContent).toContain("(50)");
    expect(container.textContent).toContain("oauth");
  });
  it("clicks tag", () => {
    const fn = vi.fn();
    const { container } = render(<TagCloud tags={tags} onTagClick={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("webhook");
  });
  it("active tag highlighted", () => {
    const { container } = render(<TagCloud tags={tags} onTagClick={vi.fn()} activeTag="api" />);
    const apiBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("api"));
    expect(apiBtn?.className).toContain("bg-blue-600");
  });
});
