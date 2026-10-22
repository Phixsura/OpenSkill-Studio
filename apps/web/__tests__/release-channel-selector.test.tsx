import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReleaseChannelSelector } from "@/components/release-channel-selector";

describe("ReleaseChannelSelector", () => {
  const channels = [
    { channel: "stable", version: "1.0.0", released_at: "2026-01-01" },
    { channel: "beta", version: "2.0.0-beta", released_at: "2026-06-01" },
  ];
  it("renders channels", () => {
    const { container } = render(<ReleaseChannelSelector channels={channels} selected="stable" onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Stable");
    expect(container.textContent).toContain("Beta");
    expect(container.textContent).toContain("1.0.0");
  });
  it("calls onSelect", () => {
    const fn = vi.fn();
    const { container } = render(<ReleaseChannelSelector channels={channels} selected="stable" onSelect={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]);
    expect(fn).toHaveBeenCalledWith("beta");
  });
});
