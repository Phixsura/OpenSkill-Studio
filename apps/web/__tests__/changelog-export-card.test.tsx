import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogExportCard from "../src/components/changelog-export-card";

const formats = [
  { format: "markdown", entry_count: 50, size_bytes: 4096, available: true },
  { format: "json", entry_count: 50, size_bytes: 8192, available: true },
  { format: "csv", entry_count: 50, size_bytes: 2048, available: false },
];

describe("ChangelogExportCard", () => {
  it("renders header", () => {
    const { container } = render(<ChangelogExportCard formats={formats} appName="My App" />);
    expect(container.textContent).toContain("Export Changelog");
  });

  it("renders format names", () => {
    const { container } = render(<ChangelogExportCard formats={formats} appName="App" />);
    expect(container.textContent).toContain("markdown");
    expect(container.textContent).toContain("json");
    expect(container.textContent).toContain("csv");
  });

  it("shows entry count and size", () => {
    const { container } = render(<ChangelogExportCard formats={formats} appName="App" />);
    expect(container.textContent).toContain("50 entries");
    expect(container.textContent).toContain("4.0 KB");
  });

  it("shows format icons", () => {
    const { container } = render(<ChangelogExportCard formats={formats} appName="App" />);
    expect(container.textContent).toContain("📝");
    expect(container.textContent).toContain("📋");
  });

  it("shows empty state", () => {
    const { container } = render(<ChangelogExportCard formats={[]} appName="App" />);
    expect(container.textContent).toContain("No export formats");
  });
});
