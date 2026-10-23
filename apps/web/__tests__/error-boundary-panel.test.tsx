import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorBoundaryPanel } from "@/components/error-boundary-panel";

describe("ErrorBoundaryPanel", () => {
  const groups = [
    { fingerprint: "abc", count: 5, type: "ValueError", message: "bad input", last_seen: "2026-01-02T00:00:00Z" },
    { fingerprint: "def", count: 1, type: "TypeError", message: "null ref", last_seen: "2026-01-01T00:00:00Z" },
  ];
  it("renders error groups", () => {
    const { container } = render(<ErrorBoundaryPanel groups={groups} totalErrors={6} uniqueErrors={2} />);
    expect(container.textContent).toContain("ValueError");
    expect(container.textContent).toContain("bad input");
    expect(container.textContent).toContain("5×");
    expect(container.textContent).toContain("6 total");
    expect(container.textContent).toContain("2 unique");
  });
  it("shows empty state", () => {
    const { container } = render(<ErrorBoundaryPanel groups={[]} totalErrors={0} uniqueErrors={0} />);
    expect(container.textContent).toContain("No errors");
  });
});
