import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TagInput } from "@/components/tag-input";

describe("TagInput", () => {
  it("shows existing tags", () => {
    const { container } = render(<TagInput tags={["analytics", "dashboard"]} onChange={vi.fn()} />);
    expect(container.textContent).toContain("analytics");
    expect(container.textContent).toContain("dashboard");
  });

  it("shows count", () => {
    const { container } = render(<TagInput tags={["a", "b"]} onChange={vi.fn()} maxTags={5} />);
    expect(container.textContent).toContain("2/5");
  });

  it("has input and add button", () => {
    const { container } = render(<TagInput tags={[]} onChange={vi.fn()} />);
    expect(container.querySelector("input")).toBeTruthy();
    expect(container.textContent).toContain("Add");
  });

  it("has remove buttons", () => {
    const { container } = render(<TagInput tags={["x"]} onChange={vi.fn()} />);
    expect(container.textContent).toContain("×");
  });
});
