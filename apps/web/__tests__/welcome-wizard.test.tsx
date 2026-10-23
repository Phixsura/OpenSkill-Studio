import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WelcomeWizard } from "@/components/welcome-wizard";

describe("WelcomeWizard", () => {
  const steps = [
    { title: "Welcome!", content: "Let's get started" },
    { title: "Create App", action: "create_app" },
    { title: "All Done!", content: "You're ready" },
  ];
  it("renders first step", () => {
    const { container } = render(<WelcomeWizard steps={steps} experience="beginner" onComplete={vi.fn()} />);
    expect(container.textContent).toContain("Welcome!");
    expect(container.textContent).toContain("1 / 3");
  });
  it("navigates forward", () => {
    const { container } = render(<WelcomeWizard steps={steps} experience="beginner" onComplete={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Next"))!);
    expect(container.textContent).toContain("Create App");
    expect(container.textContent).toContain("2 / 3");
  });
  it("completes on last step", () => {
    const fn = vi.fn();
    const { container } = render(<WelcomeWizard steps={[{ title: "Done" }]} experience="expert" onComplete={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Get Started"))!);
    expect(fn).toHaveBeenCalled();
  });
});
