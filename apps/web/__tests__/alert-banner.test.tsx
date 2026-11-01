import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AlertBanner } from "@/components/alert-banner";

describe("AlertBanner", () => {
  it("renders", () => {
    const { container } = render(
      <AlertBanner message="Update available" title="New Version" variant="info"
        icon="ℹ️" bgClass="bg-blue-50" dismissible={true} action={null} onDismiss={vi.fn()} />
    );
    expect(container.textContent).toContain("ℹ️");
    expect(container.textContent).toContain("New Version");
    expect(container.textContent).toContain("Update available");
    expect(container.textContent).toContain("✕");
  });
  it("dismiss", () => {
    const fn = vi.fn();
    const { container } = render(
      <AlertBanner message="X" title={null} variant="info" icon="ℹ️" bgClass=""
        dismissible={true} action={null} onDismiss={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "✕")!);
    expect(fn).toHaveBeenCalled();
  });
  it("with action", () => {
    const fn = vi.fn();
    const { container } = render(
      <AlertBanner message="Update" title={null} variant="info" icon="ℹ️" bgClass=""
        dismissible={false} action={{ label: "Update Now", url: "/update" }}
        onDismiss={vi.fn()} onAction={fn} />
    );
    expect(container.textContent).toContain("Update Now →");
  });
});
