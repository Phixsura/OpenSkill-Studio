import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GettingStartedPanel } from "@/components/getting-started-panel";

const items = [
  { itemId: "account", title: "Create Account", description: "Sign up", helpUrl: "/docs", completed: true },
  { itemId: "cli", title: "Install CLI", description: "Install tools", helpUrl: "/docs", completed: false },
  { itemId: "scaffold", title: "Scaffold", description: "Create project", helpUrl: "/docs", completed: false },
];
const progress = { completed: 1, total: 3, percent: 33, nextStep: "Install CLI", allDone: false };

describe("GettingStartedPanel", () => {
  it("renders checklist", () => {
    const { container } = render(<GettingStartedPanel items={items} progress={progress} />);
    expect(container.textContent).toContain("Create Account");
    expect(container.textContent).toContain("Install CLI");
    expect(container.textContent).toContain("1/3");
  });

  it("calls onComplete", () => {
    const fn = vi.fn();
    const { getByText } = render(<GettingStartedPanel items={items} progress={progress} onComplete={fn} />);
    // Click the uncompleted item's circle button - find by text content nearby
    const buttons = document.querySelectorAll("button");
    const unchecked = Array.from(buttons).find(b => !b.textContent?.includes("✓") && b.className.includes("rounded-full") && b.className.includes("border-2"));
    if (unchecked) fireEvent.click(unchecked);
    expect(fn).toHaveBeenCalled();
  });

  it("shows completion state", () => {
    const done = { completed: 3, total: 3, percent: 100, nextStep: null, allDone: true };
    const { container } = render(<GettingStartedPanel items={items} progress={done} />);
    expect(container.textContent).toContain("all set");
  });
});
