import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DownloadStatsCard } from "@/components/download-stats-card";

describe("DownloadStatsCard", () => {
  it("shows total", () => {
    const { container } = render(<DownloadStatsCard total={5000} byPlatform={{ npm: 3000, pip: 2000 }} byVersion={{}} />);
    expect(container.textContent).toContain("5,000");
  });
  it("shows platforms", () => {
    const { container } = render(<DownloadStatsCard total={100} byPlatform={{ npm: 80, pip: 20 }} byVersion={{}} />);
    expect(container.textContent).toContain("npm");
    expect(container.textContent).toContain("pip");
  });
});
