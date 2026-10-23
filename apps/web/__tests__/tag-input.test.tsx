import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TagInput } from "@/components/tag-input";

describe("TagInput", () => {
  it("renders tags", () => {
    const { container } = render(
      <TagInput tags={["api", "tools"]} suggestions={[]} onAdd={vi.fn()} onRemove={vi.fn()} maxTags={10} />
    );
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("tools");
    expect(container.textContent).toContain("2/10");
  });
  it("remove tag", () => {
    const fn = vi.fn();
    const { container } = render(
      <TagInput tags={["api"]} suggestions={[]} onAdd={vi.fn()} onRemove={fn} maxTags={10} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("api");
  });
});
