import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DevToolkitPanel } from "@/components/dev-toolkit-panel";

describe("DevToolkitPanel", () => {
  it("renders toolkit", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <DevToolkitPanel onSelect={onSelect} tools={[
        { id: "gen", name: "Test Data", icon: "🎲", description: "Generate test data" },
        { id: "fmt", name: "JSON Format", icon: "📋", description: "Format JSON" },
      ]} />
    );
    expect(container.textContent).toContain("Developer Toolkit");
    expect(container.textContent).toContain("Test Data");
    expect(container.textContent).toContain("JSON Format");
    fireEvent.click(getByText("Test Data"));
    expect(onSelect).toHaveBeenCalledWith("gen");
  });
});
