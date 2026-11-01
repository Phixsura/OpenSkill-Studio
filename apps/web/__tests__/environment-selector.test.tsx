import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvironmentSelector } from "@/components/environment-selector";

describe("EnvironmentSelector", () => {
  it("renders selector", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <EnvironmentSelector selected="staging" onSelect={onSelect} environments={[
        { id: "staging", label: "Staging", icon: "🧪", protected: false },
        { id: "production", label: "Production", icon: "🚀", protected: true },
      ]} />
    );
    expect(container.textContent).toContain("Staging");
    expect(container.textContent).toContain("Production");
    fireEvent.click(getByText("Production"));
    expect(onSelect).toHaveBeenCalledWith("production");
  });
});
