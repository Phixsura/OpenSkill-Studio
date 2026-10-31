import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReleaseChannelPanel } from "@/components/release-channel-panel";

const MOCK_CHANNELS = [
  {
    channel: "stable" as const,
    latest_version: "1.0.0",
    history: [{ version: "1.0.0", published_at: "2026-10-20T00:00:00Z", notes: "Initial release" }],
  },
  {
    channel: "beta" as const,
    latest_version: "1.1.0-beta.2",
    history: [
      { version: "1.1.0-beta.2", published_at: "2026-10-25T00:00:00Z", notes: "Fix auth" },
      { version: "1.1.0-beta.1", published_at: "2026-10-22T00:00:00Z", notes: "New dashboard" },
    ],
  },
  {
    channel: "canary" as const,
    latest_version: "1.2.0-alpha.1",
    history: [{ version: "1.2.0-alpha.1", published_at: "2026-10-27T00:00:00Z", notes: "" }],
  },
  {
    channel: "internal" as const,
    latest_version: null,
    history: [],
  },
];

const defaultProps = {
  appName: "LMS Connector",
  channels: MOCK_CHANNELS,
  currentSubscription: "stable",
  pinnedVersion: null as string | null,
  onPromote: vi.fn(),
  onRollback: vi.fn(),
  onSubscribe: vi.fn(),
};

describe("ReleaseChannelPanel", () => {
  it("renders heading and app name", () => {
    const { container } = render(<ReleaseChannelPanel {...defaultProps} />);
    expect(container.textContent).toContain("Release Channels");
    expect(container.textContent).toContain("LMS Connector");
  });

  it("renders channel names", () => {
    const { container } = render(<ReleaseChannelPanel {...defaultProps} />);
    expect(container.textContent).toContain("stable");
    expect(container.textContent).toContain("beta");
    expect(container.textContent).toContain("canary");
    expect(container.textContent).toContain("internal");
  });

  it("renders latest versions", () => {
    const { container } = render(<ReleaseChannelPanel {...defaultProps} />);
    expect(container.textContent).toContain("1.0.0");
    expect(container.textContent).toContain("1.1.0-beta.2");
    expect(container.textContent).toContain("1.2.0-alpha.1");
  });

  it("shows No releases for empty channel", () => {
    const { container } = render(<ReleaseChannelPanel {...defaultProps} />);
    expect(container.textContent).toContain("No releases");
  });

  it("shows SUBSCRIBED badge", () => {
    const { container } = render(<ReleaseChannelPanel {...defaultProps} />);
    expect(container.textContent).toContain("SUBSCRIBED");
  });

  it("shows subscription info", () => {
    const { container } = render(<ReleaseChannelPanel {...defaultProps} />);
    expect(container.textContent).toContain("Subscribed to");
  });

  it("shows pinned version", () => {
    const { container } = render(<ReleaseChannelPanel {...defaultProps} pinnedVersion="0.9.0" />);
    expect(container.textContent).toContain("Pinned: 0.9.0");
  });

  it("shows promote button for non-stable channels", () => {
    const { container } = render(<ReleaseChannelPanel {...defaultProps} />);
    const promBtns = Array.from(container.querySelectorAll("button")).filter((b) =>
      b.textContent?.includes("→"),
    );
    assert(promBtns.length >= 2); // beta→stable, canary→beta
  });

  it("calls onPromote", () => {
    const onPromote = vi.fn();
    const { container } = render(<ReleaseChannelPanel {...defaultProps} onPromote={onPromote} />);
    const btn = Array.from(container.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("→ stable"),
    );
    fireEvent.click(btn!);
    expect(onPromote).toHaveBeenCalledWith("beta", "stable");
  });

  it("shows rollback for channels with 2+ releases", () => {
    const { container } = render(<ReleaseChannelPanel {...defaultProps} />);
    const rollBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Rollback",
    );
    expect(rollBtns.length).toBe(1); // only beta has 2+ history
  });

  it("calls onRollback", () => {
    const onRollback = vi.fn();
    const { container } = render(<ReleaseChannelPanel {...defaultProps} onRollback={onRollback} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Rollback",
    );
    fireEvent.click(btn!);
    expect(onRollback).toHaveBeenCalledWith("beta");
  });

  it("calls onSubscribe for non-subscribed channel", () => {
    const onSubscribe = vi.fn();
    const { container } = render(
      <ReleaseChannelPanel {...defaultProps} onSubscribe={onSubscribe} />,
    );
    const subBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Subscribe",
    );
    fireEvent.click(subBtns[0]);
    expect(onSubscribe).toHaveBeenCalled();
  });

  it("renders release history", () => {
    const { container } = render(<ReleaseChannelPanel {...defaultProps} />);
    expect(container.textContent).toContain("Fix auth");
    expect(container.textContent).toContain("New dashboard");
  });
});
