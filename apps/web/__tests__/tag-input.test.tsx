import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TagInput } from "@/components/tag-input";

describe("TagInput", () => {
  it("renders tags", () => {
    const onRemove = vi.fn();
    const { container, getAllByText } = render(
      <TagInput tags={["python", "api"]} maxTags={10} onAdd={vi.fn()} onRemove={onRemove} />
    );
    expect(container.textContent).toContain("python");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("2/10 tags");
    fireEvent.click(getAllByText("×")[0]);
    expect(onRemove).toHaveBeenCalledWith("python");
  });
});
