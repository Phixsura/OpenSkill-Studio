import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WelcomeFlow } from "@/components/welcome-flow";

const steps = [
  { stepId: "explore", title: "Explore", content: "Browse marketplace", actionLabel: "Browse", completed: false },
  { stepId: "install", title: "Install", content: "Install an extension", actionLabel: "Install", completed: false },
];
const progress = { completed: 0, total: 2, percentage: 0, allDone: false };

describe("WelcomeFlow", () => {
  it("renders welcome", () => {
    const { container } = render(<WelcomeFlow steps={steps} progress={progress} />);
    expect(container.textContent).toContain("Welcome to OpenSkill");
    expect(container.textContent).toContain("Explore");
    expect(container.textContent).toContain("0/2");
  });
  it("hides when done", () => {
    const { container } = render(<WelcomeFlow steps={[]} progress={{ completed: 2, total: 2, percentage: 100, allDone: true }} />);
    expect(container.textContent).toBe("");
  });
  it("complete step", () => {
    const fn = vi.fn();
    const { container } = render(<WelcomeFlow steps={steps} progress={progress} onComplete={fn} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Browse");
    if (btn) fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith("explore");
  });
});
