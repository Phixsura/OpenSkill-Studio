import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TabBar } from "@/components/tab-bar";

describe("TabBar", () => {
  it("renders tabs", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <TabBar onSelect={onSelect} tabs={[
        { id: "overview", label: "Overview", icon: "📊", badge: null, active: true, disabled: false },
        { id: "logs", label: "Logs", icon: "📋", badge: 5, active: false, disabled: false },
        { id: "admin", label: "Admin", icon: "🔒", badge: null, active: false, disabled: true },
      ]} />
    );
    expect(container.textContent).toContain("Overview");
    expect(container.textContent).toContain("Logs");
    expect(container.textContent).toContain("5");
    fireEvent.click(getByText("Logs"));
    expect(onSelect).toHaveBeenCalledWith("logs");
  });
});
