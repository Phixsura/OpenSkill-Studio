import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CommandPalette } from "@/components/command-palette";

const commands = [
  { commandId: "nav-home", label: "Go to Home", category: "navigation", shortcut: "⌘H", icon: "🏠", handler: "/" },
  { commandId: "action-deploy", label: "Deploy", category: "action", shortcut: "⌘⇧D", icon: "🚀", handler: "/deploy" },
];

describe("CommandPalette", () => {
  it("renders when open", () => {
    const { container } = render(<CommandPalette commands={commands} open />);
    expect(container.textContent).toContain("Go to Home");
    expect(container.textContent).toContain("Deploy");
    expect(container.textContent).toContain("⌘H");
  });
  it("hidden when closed", () => {
    const { container } = render(<CommandPalette commands={commands} open={false} />);
    expect(container.textContent).toBe("");
  });
  it("execute command", () => {
    const fn = vi.fn();
    const { container } = render(<CommandPalette commands={commands} open onExecute={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[0]);
    expect(fn).toHaveBeenCalledWith("/");
  });
});
