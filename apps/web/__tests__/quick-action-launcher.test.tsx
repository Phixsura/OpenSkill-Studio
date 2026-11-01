import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickActionLauncher } from "@/components/quick-action-launcher";

describe("QuickActionLauncher", () => {
  it("renders actions", () => {
    const { container } = render(
      <QuickActionLauncher onExecute={vi.fn()} actions={[
        { id: "deploy", label: "Deploy", icon: "🚀", category: "deployment", shortcut: "⌘+D" },
        { id: "incident", label: "Incident", icon: "🚨", category: "ops", shortcut: "⌘+I" },
      ]} />
    );
    expect(container.textContent).toContain("Quick Actions");
    expect(container.textContent).toContain("Deploy");
    expect(container.textContent).toContain("Incident");
    expect(container.textContent).toContain("⌘+D");
  });
});
