import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PluginRegistryPanel } from "@/components/plugin-registry-panel";

const mockPlugins = [
  { pluginId: "p1", name: "chart-plugin", version: "1.0", description: "Charts",
    tags: ["ui"], enabled: true, dependencies: [] },
  { pluginId: "p2", name: "auth-plugin", version: "2.0", description: "Auth",
    tags: ["security"], enabled: false, dependencies: ["core"] },
];

describe("PluginRegistryPanel", () => {
  it("renders plugins", () => {
    const { container } = render(<PluginRegistryPanel plugins={mockPlugins} />);
    expect(container.textContent).toContain("chart-plugin");
    expect(container.textContent).toContain("1/2 enabled");
  });

  it("shows dependencies", () => {
    const { container } = render(<PluginRegistryPanel plugins={mockPlugins} />);
    expect(container.textContent).toContain("deps: core");
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { getAllByText } = render(<PluginRegistryPanel plugins={mockPlugins} onToggle={onToggle} />);
    fireEvent.click(getAllByText("Off")[0]);
    expect(onToggle).toHaveBeenCalledWith("auth-plugin");
  });
});
