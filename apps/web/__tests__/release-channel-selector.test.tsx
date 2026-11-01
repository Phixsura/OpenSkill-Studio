import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReleaseChannelSelector } from "@/components/release-channel-selector";

describe("ReleaseChannelSelector", () => {
  const channels = [
    { id: "stable", label: "Stable", icon: "✅", current_version: "1.0.0", has_release: true, risk: "low" },
    { id: "beta", label: "Beta", icon: "🧪", current_version: "1.1.0-beta", has_release: true, risk: "medium" },
  ];
  it("renders", () => {
    const { container } = render(
      <ReleaseChannelSelector channels={channels} selectedChannel="stable" onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Release Channels");
    expect(container.textContent).toContain("Stable");
    expect(container.textContent).toContain("v1.0.0");
    expect(container.textContent).toContain("Beta");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(
      <ReleaseChannelSelector channels={channels} selectedChannel="stable" onSelect={fn} />
    );
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]);
    expect(fn).toHaveBeenCalledWith("beta");
  });
});
