import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SuccessPage } from "@/components/success-page";

describe("SuccessPage", () => {
  const steps = [
    { label: "Dashboard", url: "/dashboard", primary: true },
    { label: "Details", url: "/apps/a1", primary: false },
  ];
  it("renders", () => {
    const { container } = render(
      <SuccessPage title="Auth SDK Installed!" icon="🎉" message="Ready to use."
        nextSteps={steps} onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("🎉");
    expect(container.textContent).toContain("Auth SDK Installed!");
    expect(container.textContent).toContain("Ready to use.");
    expect(container.textContent).toContain("Dashboard");
    expect(container.textContent).toContain("Details");
  });
  it("navigate", () => {
    const fn = vi.fn();
    const { container } = render(
      <SuccessPage title="X" icon="✅" message="Y" nextSteps={steps} onNavigate={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Dashboard")!);
    expect(fn).toHaveBeenCalledWith("/dashboard");
  });
});
