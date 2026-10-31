import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PluginHooksPanel } from "@/components/plugin-hooks-panel";

const mockHooks = [
  { id: "h1", hookPoint: "post_install", handlerName: "setup_db", priority: 10, enabled: true, errorCount: 0, maxErrors: 5 },
  { id: "h2", hookPoint: "post_install", handlerName: "send_welcome", priority: 5, enabled: true, errorCount: 2, maxErrors: 5 },
  { id: "h3", hookPoint: "on_error", handlerName: "report_crash", priority: 0, enabled: false, errorCount: 5, maxErrors: 5 },
];

describe("PluginHooksPanel", () => {
  it("renders hooks grouped by point", () => {
    const { container } = render(
      <PluginHooksPanel hooks={mockHooks} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("setup_db");
    expect(container.textContent).toContain("Post Install");
    expect(container.textContent).toContain("2/3 active");
  });

  it("shows error count", () => {
    const { container } = render(
      <PluginHooksPanel hooks={mockHooks} extensionName="Test" />
    );
    expect(container.textContent).toContain("2/5 errors");
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { getAllByText } = render(
      <PluginHooksPanel hooks={mockHooks} extensionName="Test" onToggle={onToggle} />
    );
    fireEvent.click(getAllByText("Off")[0]);
    expect(onToggle).toHaveBeenCalledWith("h3");
  });
});
