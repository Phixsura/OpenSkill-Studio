import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfigHotReloadPanel } from "@/components/config-hot-reload-panel";

const mockConfig = { theme: "dark", debug: "false", port: "3000" };
const mockHistory = [
  { changeId: "c1", key: "theme", oldValue: "light", newValue: "dark",
    applied: true, rolledBack: false, timestamp: "12:00" },
  { changeId: "c2", key: "debug", oldValue: "true", newValue: "false",
    applied: true, rolledBack: true, timestamp: "12:05" },
];

describe("ConfigHotReloadPanel", () => {
  it("renders current config", () => {
    const { container } = render(
      <ConfigHotReloadPanel currentConfig={mockConfig} history={[]} subscribers={["on_update"]} />
    );
    expect(container.textContent).toContain("theme");
    expect(container.textContent).toContain("dark");
    expect(container.textContent).toContain("Config (3)");
  });

  it("shows change history", () => {
    const { getByText, container } = render(
      <ConfigHotReloadPanel currentConfig={mockConfig} history={mockHistory} subscribers={[]} />
    );
    fireEvent.click(getByText("History (2)"));
    expect(container.textContent).toContain("light");
    expect(container.textContent).toContain("→");
    expect(container.textContent).toContain("rolled back");
  });

  it("calls onRollback", () => {
    const onRollback = vi.fn();
    const { getByText } = render(
      <ConfigHotReloadPanel currentConfig={mockConfig} history={mockHistory} subscribers={[]} onRollback={onRollback} />
    );
    fireEvent.click(getByText("History (2)"));
    fireEvent.click(getByText("Undo"));
    expect(onRollback).toHaveBeenCalledWith("c1");
  });

  it("shows subscriber count", () => {
    const { container } = render(
      <ConfigHotReloadPanel currentConfig={mockConfig} history={[]} subscribers={["a", "b"]} />
    );
    expect(container.textContent).toContain("2 subscribers");
  });
});
