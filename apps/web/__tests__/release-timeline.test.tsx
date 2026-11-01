import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseTimeline } from "@/components/release-timeline";

describe("ReleaseTimeline", () => {
  it("renders timeline", () => {
    const { container } = render(
      <ReleaseTimeline releases={[
        { version: "3.5.0", date: "2026-10-24", title: "SSO & Dark Mode",
          changesCount: 3, breakingCount: 1, highlight: true, tags: ["major"] },
        { version: "3.4.1", date: "2026-10-20", title: "Bug fixes",
          changesCount: 1, breakingCount: 0, highlight: false, tags: [] },
      ]} />
    );
    expect(container.textContent).toContain("v3.5.0");
    expect(container.textContent).toContain("SSO & Dark Mode");
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("major");
    expect(container.textContent).toContain("v3.4.1");
  });
});
