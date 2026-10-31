import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionChangelogViewer } from "@/components/extension-changelog-viewer";

const mockEntries = [
  {
    version: "2.1.0", date: "2026-10-25",
    changes: [
      { type: "added" as const, description: "Dark mode support" },
      { type: "fixed" as const, description: "Memory leak on large files" },
    ],
  },
  {
    version: "2.0.0", date: "2026-10-20",
    changes: [
      { type: "changed" as const, description: "Complete UI redesign" },
      { type: "removed" as const, description: "Legacy API endpoints" },
    ],
  },
  {
    version: "1.0.1", date: "2026-10-15",
    changes: [{ type: "fixed" as const, description: "Crash on startup" }],
    yanked: true,
  },
];

describe("ExtensionChangelogViewer", () => {
  it("renders extension name and versions", () => {
    const { container } = render(
      <ExtensionChangelogViewer extensionName="Code Formatter" entries={mockEntries} />
    );
    expect(container.textContent).toContain("Code Formatter Changelog");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("v1.0.1");
  });

  it("shows latest version expanded by default", () => {
    const { container } = render(
      <ExtensionChangelogViewer extensionName="Test" entries={mockEntries} />
    );
    expect(container.textContent).toContain("Dark mode support");
    expect(container.textContent).toContain("Memory leak");
  });

  it("toggles version expansion", () => {
    const { getByText, container } = render(
      <ExtensionChangelogViewer extensionName="Test" entries={mockEntries} />
    );
    fireEvent.click(getByText("v2.0.0"));
    expect(container.textContent).toContain("Complete UI redesign");
  });

  it("shows yanked badge", () => {
    const { container } = render(
      <ExtensionChangelogViewer extensionName="Test" entries={mockEntries} />
    );
    expect(container.textContent).toContain("Yanked");
  });
});
