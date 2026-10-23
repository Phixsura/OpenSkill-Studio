import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ToastContainer } from "@/components/toast-container";

describe("ToastContainer", () => {
  it("renders toasts", () => {
    const onDismiss = vi.fn();
    const { container, getAllByText } = render(
      <ToastContainer onDismiss={onDismiss} toasts={[
        { id: "t1", title: "Saved!", message: "", variant: "success", icon: "✅", dismissible: true },
        { id: "t2", title: "Error", message: "Connection lost", variant: "error", icon: "❌", dismissible: true },
      ]} />
    );
    expect(container.textContent).toContain("Saved!");
    expect(container.textContent).toContain("Error");
    expect(container.textContent).toContain("Connection lost");
    fireEvent.click(getAllByText("✕")[0]);
    expect(onDismiss).toHaveBeenCalledWith("t1");
  });
});
