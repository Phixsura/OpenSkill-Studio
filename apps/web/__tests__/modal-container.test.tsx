import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ModalContainer } from "@/components/modal-container";

describe("ModalContainer", () => {
  it("renders", () => {
    const { container } = render(
      <ModalContainer title="Confirm" sizeClass="max-w-md" dismissible={true}
        hasFooter={true} onClose={vi.fn()} onConfirm={vi.fn()}>
        <p>Are you sure?</p>
      </ModalContainer>
    );
    expect(container.textContent).toContain("Confirm");
    expect(container.textContent).toContain("Are you sure?");
    expect(container.textContent).toContain("Cancel");
    expect(container.textContent).toContain("Confirm");
  });
  it("close", () => {
    const fn = vi.fn();
    const { container } = render(
      <ModalContainer title="X" sizeClass="max-w-sm" dismissible={true}
        hasFooter={false} onClose={fn}>
        <p>Content</p>
      </ModalContainer>
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "✕")!);
    expect(fn).toHaveBeenCalled();
  });
});
