import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotFoundAnalytics } from "@/components/not-found-analytics";

describe("NotFoundAnalytics", () => {
  it("renders analytics", () => {
    const { container } = render(
      <NotFoundAnalytics total={50} uniquePaths={15}
        topPaths={[{ path: "/old-page", count: 20 }]}
        topReferrers={[{ referrer: "google.com", count: 15 }]}
        needsAttention={true} />
    );
    expect(container.textContent).toContain("404 Analytics");
    expect(container.textContent).toContain("/old-page");
    expect(container.textContent).toContain("20×");
    expect(container.textContent).toContain("google.com");
    expect(container.textContent).toContain("Needs attention");
  });
});
