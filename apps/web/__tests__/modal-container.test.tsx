import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ModalContainer } from "@/components/modal-container";

describe("ModalContainer", () => {
  it("renders when open", () => {
    const { container } = render(
      <ModalContainer open={true} title="Test Modal" onClose={vi.fn()}>
        <p>Modal content</p>
      </ModalContainer>
    );
    expect(container.textContent).toContain("Test Modal");
    expect(container.textContent).toContain("Modal content");
  });
  it("hidden when closed", () => {
    const { container } = render(
      <ModalContainer open={false} title="Hidden" onClose={vi.fn()}>
        <p>Content</p>
      </ModalContainer>
    );
    expect(container.innerHTML).toBe("");
  });
  it("closes on X", () => {
    const fn = vi.fn();
    const { container } = render(
      <ModalContainer open={true} title="X" onClose={fn}><p>C</p></ModalContainer>
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
