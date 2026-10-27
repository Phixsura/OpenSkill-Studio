import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LicenseStatusCard } from "@/components/license-status-card";

const ACTIVE_LICENSE = {
  license_key: "OSK-ABCD1234-1111-2222-3333-4444",
  app_name: "Pro Analytics",
  license_type: "subscription" as const,
  status: "active" as const,
  max_seats: 10,
  active_seats: 3,
  days_remaining: 45,
  issued_at: "2026-09-01T00:00:00Z",
  expires_at: "2027-09-01T00:00:00Z",
};

const EXPIRED_LICENSE = {
  ...ACTIVE_LICENSE,
  status: "expired" as const,
  days_remaining: 0,
};

const PERPETUAL = {
  ...ACTIVE_LICENSE,
  license_type: "perpetual" as const,
  expires_at: null,
  days_remaining: null,
};

describe("LicenseStatusCard", () => {
  it("renders app name", () => {
    const { container } = render(
      <LicenseStatusCard license={ACTIVE_LICENSE} onDeactivate={vi.fn()} onRenew={vi.fn()} />,
    );
    expect(container.textContent).toContain("Pro Analytics");
  });

  it("renders license type", () => {
    const { container } = render(
      <LicenseStatusCard license={ACTIVE_LICENSE} onDeactivate={vi.fn()} onRenew={vi.fn()} />,
    );
    expect(container.textContent).toContain("Subscription License");
  });

  it("renders active status badge", () => {
    const { container } = render(
      <LicenseStatusCard license={ACTIVE_LICENSE} onDeactivate={vi.fn()} onRenew={vi.fn()} />,
    );
    expect(container.textContent).toContain("Active");
  });

  it("renders license key", () => {
    const { container } = render(
      <LicenseStatusCard license={ACTIVE_LICENSE} onDeactivate={vi.fn()} onRenew={vi.fn()} />,
    );
    expect(container.textContent).toContain("OSK-ABCD1234");
  });

  it("renders seat usage", () => {
    const { container } = render(
      <LicenseStatusCard license={ACTIVE_LICENSE} onDeactivate={vi.fn()} onRenew={vi.fn()} />,
    );
    expect(container.textContent).toContain("3/10");
  });

  it("renders expiry date", () => {
    const { container } = render(
      <LicenseStatusCard license={ACTIVE_LICENSE} onDeactivate={vi.fn()} onRenew={vi.fn()} />,
    );
    expect(container.textContent).toContain("2027");
  });

  it("renders Never for perpetual", () => {
    const { container } = render(
      <LicenseStatusCard license={PERPETUAL} onDeactivate={vi.fn()} onRenew={vi.fn()} />,
    );
    expect(container.textContent).toContain("Never");
    expect(container.textContent).toContain("Perpetual");
  });

  it("shows Deactivate for active license", () => {
    const onDeactivate = vi.fn();
    const { container } = render(
      <LicenseStatusCard license={ACTIVE_LICENSE} onDeactivate={onDeactivate} onRenew={vi.fn()} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Deactivate",
    );
    expect(btn).toBeTruthy();
    fireEvent.click(btn!);
    expect(onDeactivate).toHaveBeenCalledOnce();
  });

  it("shows Renew for expired license", () => {
    const onRenew = vi.fn();
    const { container } = render(
      <LicenseStatusCard license={EXPIRED_LICENSE} onDeactivate={vi.fn()} onRenew={onRenew} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Renew",
    );
    expect(btn).toBeTruthy();
    fireEvent.click(btn!);
    expect(onRenew).toHaveBeenCalledOnce();
  });

  it("hides Deactivate for expired", () => {
    const { container } = render(
      <LicenseStatusCard license={EXPIRED_LICENSE} onDeactivate={vi.fn()} onRenew={vi.fn()} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Deactivate",
    );
    expect(btn).toBeFalsy();
  });

  it("renders days remaining warning", () => {
    const nearExpiry = { ...ACTIVE_LICENSE, days_remaining: 5 };
    const { container } = render(
      <LicenseStatusCard license={nearExpiry} onDeactivate={vi.fn()} onRenew={vi.fn()} />,
    );
    expect(container.textContent).toContain("5d remaining");
  });

  it("renders expired badge", () => {
    const { container } = render(
      <LicenseStatusCard license={EXPIRED_LICENSE} onDeactivate={vi.fn()} onRenew={vi.fn()} />,
    );
    expect(container.textContent).toContain("Expired");
  });
});
