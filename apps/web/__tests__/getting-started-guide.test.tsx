import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GettingStartedGuide } from "@/components/getting-started-guide";

describe("GettingStartedGuide", () => {
  it("renders guides", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <GettingStartedGuide recommended="build_app" onSelect={onSelect} guides={[
        { id: "build_app", title: "Build Your First App", icon: "📱", stepCount: 4 },
        { id: "integrate_api", title: "Integrate the API", icon: "🔌", stepCount: 4 },
      ]} />
    );
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("Build Your First App");
    expect(container.textContent).toContain("Recommended");
    expect(container.textContent).toContain("4 steps");
    fireEvent.click(getByText("Build Your First App"));
    expect(onSelect).toHaveBeenCalledWith("build_app");
  });
});
