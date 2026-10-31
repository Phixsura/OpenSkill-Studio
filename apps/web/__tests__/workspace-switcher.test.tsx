import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkspaceSwitcher } from "@/components/workspace-switcher";

describe("WorkspaceSwitcher", () => {
  const workspaces = [{ name: "Main", app_count: 3 }, { name: "Side", app_count: 1 }];
  it("renders", () => {
    const { container } = render(
      <WorkspaceSwitcher workspaces={workspaces} active="Main" onSwitch={vi.fn()} onCreate={vi.fn()} />
    );
    expect(container.textContent).toContain("Main");
    expect(container.textContent).toContain("3 apps");
  });
  it("switches", () => {
    const fn = vi.fn();
    const { container } = render(
      <WorkspaceSwitcher workspaces={workspaces} active="Main" onSwitch={fn} onCreate={vi.fn()} />
    );
    fireEvent.click(container.querySelectorAll("button")[2]); // Side
    expect(fn).toHaveBeenCalledWith("Side");
  });
});
