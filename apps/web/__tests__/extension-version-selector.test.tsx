import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionVersionSelector } from "@/components/extension-version-selector";

const mockVersions = [
  { version: "3.0.0", publishedAt: "Oct 25", status: "latest" as const, changelog: "Major redesign", size: "2.1MB" },
  { version: "2.1.0", publishedAt: "Oct 10", status: "stable" as const, changelog: "Bug fixes", size: "1.8MB" },
  { version: "2.0.0-beta", publishedAt: "Sep 20", status: "beta" as const, changelog: "Beta features", size: "1.9MB" },
  { version: "1.0.0", publishedAt: "Aug 1", status: "deprecated" as const, changelog: "Initial release", size: "1.2MB" },
];

describe("ExtensionVersionSelector", () => {
  it("renders versions with badges", () => {
    const { container } = render(
      <ExtensionVersionSelector versions={mockVersions} currentVersion="2.1.0" />
    );
    expect(container.textContent).toContain("v3.0.0");
    expect(container.textContent).toContain("Latest");
    expect(container.textContent).toContain("Deprecated");
    expect(container.textContent).toContain("✓ installed");
  });

  it("shows changelog on toggle", () => {
    const { getByText, container } = render(
      <ExtensionVersionSelector versions={mockVersions} />
    );
    fireEvent.click(getByText("Show changelog"));
    expect(container.textContent).toContain("Major redesign");
  });

  it("calls onInstall", () => {
    const onInstall = vi.fn();
    const { getByText } = render(
      <ExtensionVersionSelector versions={mockVersions} onInstall={onInstall} />
    );
    fireEvent.click(getByText("Install v3.0.0"));
    expect(onInstall).toHaveBeenCalledWith("3.0.0");
  });

  it("disables install for current version", () => {
    const { getByText } = render(
      <ExtensionVersionSelector versions={mockVersions} currentVersion="3.0.0" />
    );
    expect(getByText("✓ Currently Installed").hasAttribute("disabled") || getByText("✓ Currently Installed").closest("button")?.hasAttribute("disabled")).toBeTruthy();
  });
});
