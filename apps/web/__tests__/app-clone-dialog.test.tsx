import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppCloneDialog } from "@/components/app-clone-dialog";

describe("AppCloneDialog", () => {
  it("shows original name", () => {
    const { container } = render(<AppCloneDialog originalName="My App" onClone={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("My App");
    expect(container.textContent).toContain("Clone");
  });
  it("has inputs", () => {
    const { container } = render(<AppCloneDialog originalName="X" onClone={vi.fn()} onCancel={vi.fn()} />);
    expect(container.querySelectorAll("input").length).toBe(2);
  });
  it("pre-fills name", () => {
    const { container } = render(<AppCloneDialog originalName="Cool App" onClone={vi.fn()} onCancel={vi.fn()} />);
    const input = container.querySelector("input") as HTMLInputElement;
    expect(input?.value).toContain("Cool App");
  });
});
