import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FederationPeerCard } from "@/components/federation-peer-card";

const TRUSTED_PEER = {
  id: "peer-1",
  instance_uri: "https://school-b.openskill.io",
  display_name: "School B",
  description: "Partner training institution",
  logo_url: null,
  protocol_version: "1.0",
  trust_status: "trusted" as const,
  last_seen_at: new Date(Date.now() - 300000).toISOString(), // 5min ago
  reputation: {
    total_envelopes: 1523,
    invalid_signature_rate: 0.001,
    spam_score: 0.02,
  },
};

const PENDING_PEER = {
  ...TRUSTED_PEER,
  id: "peer-2",
  display_name: "School C",
  trust_status: "pending" as const,
  reputation: null,
  last_seen_at: null,
};

const handlers = () => ({
  onTrust: vi.fn(),
  onSuspend: vi.fn(),
  onRevoke: vi.fn(),
  onRemove: vi.fn(),
});

describe("FederationPeerCard", () => {
  it("renders peer display name and URI", () => {
    const { container } = render(<FederationPeerCard peer={TRUSTED_PEER} {...handlers()} />);
    expect(container.textContent).toContain("School B");
    expect(container.textContent).toContain("school-b.openskill.io");
  });

  it("renders trust status badge", () => {
    const { container } = render(<FederationPeerCard peer={TRUSTED_PEER} {...handlers()} />);
    expect(container.textContent).toContain("Trusted");
  });

  it("renders pending badge for pending peer", () => {
    const { container } = render(<FederationPeerCard peer={PENDING_PEER} {...handlers()} />);
    expect(container.textContent).toContain("Pending");
  });

  it("renders description when present", () => {
    const { container } = render(<FederationPeerCard peer={TRUSTED_PEER} {...handlers()} />);
    expect(container.textContent).toContain("Partner training institution");
  });

  it("renders protocol version", () => {
    const { container } = render(<FederationPeerCard peer={TRUSTED_PEER} {...handlers()} />);
    expect(container.textContent).toContain("Protocol v1.0");
  });

  it("renders reputation metrics when available", () => {
    const { container } = render(<FederationPeerCard peer={TRUSTED_PEER} {...handlers()} />);
    expect(container.textContent).toContain("Reputation");
    expect(container.textContent).toContain("Envelopes");
    expect(container.textContent).toContain("Invalid sig rate");
    expect(container.textContent).toContain("Spam score");
  });

  it("hides reputation when null", () => {
    const { container } = render(<FederationPeerCard peer={PENDING_PEER} {...handlers()} />);
    expect(container.textContent).not.toContain("Reputation");
  });

  it("shows Suspend button for trusted peer", () => {
    const h = handlers();
    const { container } = render(<FederationPeerCard peer={TRUSTED_PEER} {...h} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Suspend",
    );
    expect(btn).toBeTruthy();
    fireEvent.click(btn!);
    expect(h.onSuspend).toHaveBeenCalledWith("peer-1");
  });

  it("shows Trust button for pending peer", () => {
    const h = handlers();
    const { container } = render(<FederationPeerCard peer={PENDING_PEER} {...h} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Trust",
    );
    expect(btn).toBeTruthy();
    fireEvent.click(btn!);
    expect(h.onTrust).toHaveBeenCalledWith("peer-2");
  });

  it("shows Revoke button for pending peer", () => {
    const h = handlers();
    const { container } = render(<FederationPeerCard peer={PENDING_PEER} {...h} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Revoke",
    );
    expect(btn).toBeTruthy();
    fireEvent.click(btn!);
    expect(h.onRevoke).toHaveBeenCalledWith("peer-2");
  });

  it("always shows Remove button", () => {
    const h = handlers();
    const { container } = render(<FederationPeerCard peer={TRUSTED_PEER} {...h} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Remove",
    );
    expect(btn).toBeTruthy();
    fireEvent.click(btn!);
    expect(h.onRemove).toHaveBeenCalledWith("peer-1");
  });

  it("renders last seen as relative time", () => {
    const { container } = render(<FederationPeerCard peer={TRUSTED_PEER} {...handlers()} />);
    // Should show something like "5m ago" or "Xm ago"
    expect(container.textContent).toMatch(/Last seen:.*ago/);
  });

  it("renders 'Never' when last_seen_at is null", () => {
    const { container } = render(<FederationPeerCard peer={PENDING_PEER} {...handlers()} />);
    expect(container.textContent).toContain("Never");
  });

  it("renders default globe icon when no logo", () => {
    const { container } = render(<FederationPeerCard peer={TRUSTED_PEER} {...handlers()} />);
    expect(container.textContent).toContain("🌐");
  });

  it("renders suspended badge", () => {
    const suspended = { ...TRUSTED_PEER, trust_status: "suspended" as const };
    const { container } = render(<FederationPeerCard peer={suspended} {...handlers()} />);
    expect(container.textContent).toContain("Suspended");
  });

  it("renders revoked badge", () => {
    const revoked = { ...TRUSTED_PEER, trust_status: "revoked" as const };
    const { container } = render(<FederationPeerCard peer={revoked} {...handlers()} />);
    expect(container.textContent).toContain("Revoked");
  });
});
