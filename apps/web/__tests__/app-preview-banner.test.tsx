import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppPreviewBanner } from "@/components/app-preview-banner";

describe("AppPreviewBanner", () => {
  it("renders preview info", () => {
    const { container } = render(<AppPreviewBanner versionName="v2.0-beta" expiresAt="2026-12-01T00:00:00Z" />);
    expect(container.textContent).toContain("Preview Mode");
    expect(container.textContent).toContain("v2.0-beta");
  });
  it("publish button", () => {
    const fn = vi.fn();
    const { container } = render(<AppPreviewBanner versionName="v2" expiresAt="2026-12-01T00:00:00Z" onPublish={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
  it("no publish button if not provided", () => {
    const { container } = render(<AppPreviewBanner versionName="v2" expiresAt="2026-12-01T00:00:00Z" />);
    expect(container.querySelector("button")).toBeNull();
  });
});
