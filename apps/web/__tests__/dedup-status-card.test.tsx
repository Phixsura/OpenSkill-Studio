import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DedupStatusCard } from "@/components/dedup-status-card";

describe("DedupStatusCard", () => {
  it("renders status", () => {
    const { container } = render(
      <DedupStatusCard totalTracked={1000} activeWindow={150} duplicatesBlocked={42} windowSec={5} />
    );
    expect(container.textContent).toContain("Request Deduplication");
    expect(container.textContent).toContain("1000");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("42");
    expect(container.textContent).toContain("5s");
  });
});
