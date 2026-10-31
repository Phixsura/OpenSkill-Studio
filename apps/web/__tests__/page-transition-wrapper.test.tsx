import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PageTransitionWrapper } from "@/components/page-transition-wrapper";

describe("PageTransitionWrapper", () => {
  it("renders when shown", () => {
    const { container } = render(
      <PageTransitionWrapper transition="fade" durationMs={200} show={true}>
        <p>Page content</p>
      </PageTransitionWrapper>
    );
    expect(container.textContent).toContain("Page content");
  });
  it("hidden when not shown", () => {
    const { container } = render(
      <PageTransitionWrapper transition="fade" durationMs={0} show={false}>
        <p>Hidden</p>
      </PageTransitionWrapper>
    );
    // Initially visible=false + show=false → returns null
    expect(container.textContent).toBe("");
  });
});
