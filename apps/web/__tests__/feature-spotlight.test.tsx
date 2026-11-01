import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureSpotlight } from "@/components/feature-spotlight";

const features = [{ featureId: "f1", title: "Dark Mode", description: "New theme", icon: "🌙", category: "ui" }];

describe("FeatureSpotlight", () => {
  it("renders features", () => {
    const { container } = render(<FeatureSpotlight features={features} />);
    expect(container.textContent).toContain("Dark Mode");
  });
  it("calls onDismiss", () => {
    const fn = vi.fn();
    const { container } = render(<FeatureSpotlight features={features} onDismiss={fn} />);
    const btn = container.querySelector("button");
    if (btn) fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith("f1");
  });
});
