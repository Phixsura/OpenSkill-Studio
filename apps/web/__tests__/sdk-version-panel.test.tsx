import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SDKVersionPanel } from "@/components/sdk-version-panel";

const mockReleases = [
  { version: "3.0.0", status: "beta" as const, minPlatform: "4.0.0", maxPlatform: "5.0.0", releaseDate: "2024-06-01" },
  { version: "2.0.0", status: "stable" as const, minPlatform: "3.0.0", maxPlatform: "4.0.0", releaseDate: "2024-03-01" },
  { version: "1.0.0", status: "deprecated" as const, minPlatform: "2.0.0", maxPlatform: "3.0.0", releaseDate: "2024-01-01" },
];
const mockPath = { fromVersion: "1.0.0", toVersion: "2.0.0", steps: ["Update imports", "Run migration"], hasBreaking: true };

describe("SDKVersionPanel", () => {
  it("renders releases with status", () => {
    const { container } = render(
      <SDKVersionPanel releases={mockReleases} currentVersion="1.0.0" />
    );
    expect(container.textContent).toContain("3.0.0");
    expect(container.textContent).toContain("Stable");
    expect(container.textContent).toContain("current");
  });

  it("shows upgrade recommendation", () => {
    const onUpgrade = vi.fn();
    const { getByText } = render(
      <SDKVersionPanel releases={mockReleases} currentVersion="1.0.0"
        recommendedVersion="2.0.0" onUpgrade={onUpgrade} />
    );
    fireEvent.click(getByText("Upgrade"));
    expect(onUpgrade).toHaveBeenCalledWith("2.0.0");
  });

  it("shows migration steps", () => {
    const { container } = render(
      <SDKVersionPanel releases={mockReleases} currentVersion="1.0.0"
        upgradePath={mockPath} />
    );
    expect(container.textContent).toContain("Update imports");
    expect(container.textContent).toContain("Run migration");
    expect(mockPath.hasBreaking).toBe(true);
  });
});
