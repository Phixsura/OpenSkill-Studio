import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogDigestCard from "../src/components/api-changelog-digest-card";

const digests = [
  { digest_id: "d1", period: "weekly", period_label: "2024-W03", entry_count: 5, delivered: true },
  { digest_id: "d2", period: "daily", period_label: "2024-01-22", entry_count: 2, delivered: false },
];

describe("APIChangelogDigestCard", () => {
  it("renders header and delivered count", () => {
    const { container } = render(<APIChangelogDigestCard digests={digests} appName="App" />);
    expect(container.textContent).toContain("Changelog Digests");
    expect(container.textContent).toContain("1/2 delivered");
  });

  it("shows period labels and entry counts", () => {
    const { container } = render(<APIChangelogDigestCard digests={digests} appName="App" />);
    expect(container.textContent).toContain("2024-W03");
    expect(container.textContent).toContain("weekly");
    expect(container.textContent).toContain("5 entries");
  });

  it("shows empty state", () => {
    const { container } = render(<APIChangelogDigestCard digests={[]} appName="App" />);
    expect(container.textContent).toContain("No digests");
  });
});
