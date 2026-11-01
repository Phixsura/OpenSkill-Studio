import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickstartWizard } from "@/components/quickstart-wizard";

describe("QuickstartWizard", () => {
  const steps = [
    { id: "install", title: "Install CLI", code: "npm i -g @osk/cli", icon: "📦", order: 1, completed: true },
    { id: "login", title: "Log in", code: "osk login", icon: "🔑", order: 2, completed: false },
  ];
  it("renders steps", () => {
    const { container } = render(<QuickstartWizard steps={steps} progressPct={50} onComplete={vi.fn()} />);
    expect(container.textContent).toContain("Quickstart");
    expect(container.textContent).toContain("Install CLI");
    expect(container.textContent).toContain("Log in");
    expect(container.textContent).toContain("50%");
  });
  it("complete step", () => {
    const fn = vi.fn();
    const { container } = render(<QuickstartWizard steps={steps} progressPct={50} onComplete={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Done")!);
    expect(fn).toHaveBeenCalledWith("login");
  });
});
