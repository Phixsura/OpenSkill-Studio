import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickActionsGrid } from "@/components/quick-actions-grid";

describe("QuickActionsGrid", () => {
  it("renders actions", () => {
    const onAction = vi.fn();
    const { container, getAllByRole } = render(
      <QuickActionsGrid onAction={onAction} actions={[
        { id: "create_app", label: "Create App", icon: "📱", shortcut: "⌘N" },
        { id: "deploy", label: "Deploy", icon: "🚀", shortcut: "⌘⇧D" },
        { id: "view_logs", label: "View Logs", icon: "📋" },
      ]} />
    );
    expect(container.textContent).toContain("Quick Actions");
    expect(container.textContent).toContain("Create App");
    expect(container.textContent).toContain("⌘N");
    expect(container.textContent).toContain("Deploy");
    fireEvent.click(getAllByRole("button")[0]);
    expect(onAction).toHaveBeenCalledWith("create_app");
  });
});
