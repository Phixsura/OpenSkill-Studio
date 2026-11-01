import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ToastStack } from "@/components/toast-stack";

describe("ToastStack", () => {
  const toasts = [
    { id: "t1", message: "App published!", type: "success", icon: "✅", color: "green", actionLabel: null, dismissible: true },
    { id: "t2", message: "Update available", type: "info", icon: "ℹ️", color: "blue", actionLabel: "Update", dismissible: true },
  ];
  it("renders toasts", () => {
    const { container } = render(<ToastStack toasts={toasts} onDismiss={vi.fn()} onAction={vi.fn()} />);
    expect(container.textContent).toContain("App published!");
    expect(container.textContent).toContain("Update available");
    expect(container.textContent).toContain("Update");
  });
  it("dismiss click", () => {
    const fn = vi.fn();
    const { container } = render(<ToastStack toasts={toasts} onDismiss={fn} onAction={vi.fn()} />);
    const dismissBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "✕");
    fireEvent.click(dismissBtns[0]);
    expect(fn).toHaveBeenCalledWith("t1");
  });
});
