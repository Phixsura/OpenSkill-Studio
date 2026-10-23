import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ToastNotification } from "@/components/toast-notification";

describe("ToastNotification", () => {
  it("renders success", () => {
    const { container } = render(
      <ToastNotification message="Saved!" type="success" icon="✅"
        actionLabel={null} onDismiss={vi.fn()} />
    );
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("Saved!");
  });
  it("with action", () => {
    const fn = vi.fn();
    const { container } = render(
      <ToastNotification message="Failed" type="error" icon="❌"
        actionLabel="Retry" onAction={fn} onDismiss={vi.fn()} />
    );
    expect(container.textContent).toContain("Retry");
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Retry")!);
    expect(fn).toHaveBeenCalled();
  });
  it("dismiss", () => {
    const fn = vi.fn();
    const { container } = render(
      <ToastNotification message="X" type="info" icon="ℹ️" actionLabel={null} onDismiss={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "✕")!);
    expect(fn).toHaveBeenCalled();
  });
});
