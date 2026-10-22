import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureFlagToggle } from "@/components/feature-flag-toggle";

describe("FeatureFlagToggle", () => {
  it("renders feature name", () => {
    const { container } = render(<FeatureFlagToggle feature="sandbox_execution" enabled={true} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("sandbox execution");
  });

  it("shows description", () => {
    const { container } = render(<FeatureFlagToggle feature="f" enabled={true} onToggle={vi.fn()} description="Test desc" />);
    expect(container.textContent).toContain("Test desc");
  });

  it("has switch role", () => {
    const { container } = render(<FeatureFlagToggle feature="f" enabled={true} onToggle={vi.fn()} />);
    expect(container.querySelector("[role='switch']")).toBeTruthy();
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { container } = render(<FeatureFlagToggle feature="test_flag" enabled={true} onToggle={onToggle} />);
    fireEvent.click(container.querySelector("button")!);
    expect(onToggle).toHaveBeenCalledWith("test_flag", false);
  });

  it("aria-checked reflects state", () => {
    const { container } = render(<FeatureFlagToggle feature="f" enabled={false} onToggle={vi.fn()} />);
    expect(container.querySelector("[aria-checked='false']")).toBeTruthy();
  });
});
