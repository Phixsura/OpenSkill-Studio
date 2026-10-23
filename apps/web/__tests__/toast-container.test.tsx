import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ToastContainer } from "@/components/toast-container";

describe("ToastContainer", () => {
  const toasts = [
    { type: "success", title: "Saved!", message: "Changes saved", icon: "✅", dismissible: true },
    { type: "error", title: "Failed", message: "", icon: "❌", dismissible: true },
  ];
  it("renders toasts", () => {
    const { container } = render(<ToastContainer toasts={toasts} onDismiss={vi.fn()} />);
    expect(container.textContent).toContain("Saved!");
    expect(container.textContent).toContain("Failed");
  });
  it("dismisses", () => {
    const fn = vi.fn();
    const { container } = render(<ToastContainer toasts={toasts} onDismiss={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith(0);
  });
  it("hidden when empty", () => {
    const { container } = render(<ToastContainer toasts={[]} onDismiss={vi.fn()} />);
    expect(container.innerHTML).toBe("");
  });
});
