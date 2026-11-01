import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TrustedDeviceList } from "@/components/trusted-device-list";

describe("TrustedDeviceList", () => {
  const devices = [
    { device_id: "d1", device_name: "MacBook Pro", fingerprint_hash: "abc", registered_at: "2026-10-01", trusted_until: "2027-01-01" },
    { device_id: "d2", device_name: "iPhone 15", fingerprint_hash: "xyz", registered_at: "2026-09-01", trusted_until: "2026-12-01" },
  ];
  it("renders", () => {
    const { container } = render(
      <TrustedDeviceList devices={devices} currentDeviceId="d1" onRemove={vi.fn()} />
    );
    expect(container.textContent).toContain("Trusted Devices");
    expect(container.textContent).toContain("MacBook Pro");
    expect(container.textContent).toContain("(this device)");
    expect(container.textContent).toContain("iPhone 15");
  });
  it("remove", () => {
    const fn = vi.fn();
    const { container } = render(
      <TrustedDeviceList devices={devices} currentDeviceId="d1" onRemove={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Remove")!);
    expect(fn).toHaveBeenCalledWith("d2");
  });
});
