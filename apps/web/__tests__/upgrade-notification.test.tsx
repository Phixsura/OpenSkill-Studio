import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UpgradeNotification } from "@/components/upgrade-notification";

describe("UpgradeNotification", () => {
  it("shows versions", () => {
    const { container } = render(<UpgradeNotification appName="App" fromVersion="1.0" toVersion="2.0" breaking={false} />);
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("v1.0");
  });
  it("shows breaking warning", () => {
    const { container } = render(<UpgradeNotification appName="X" fromVersion="1.0" toVersion="2.0" breaking={true} />);
    expect(container.textContent).toContain("⚠️");
  });
  it("has upgrade button", () => {
    const { container } = render(<UpgradeNotification appName="X" fromVersion="1.0" toVersion="2.0" breaking={false} onUpgrade={vi.fn()} />);
    expect(container.textContent).toContain("Upgrade");
  });
  it("shows changelog", () => {
    const { container } = render(<UpgradeNotification appName="X" fromVersion="1.0" toVersion="2.0" breaking={false} changelog="Added webhooks" />);
    expect(container.textContent).toContain("webhooks");
  });
});
