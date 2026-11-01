import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContentModDashboard } from "@/components/content-mod-dashboard";

describe("ContentModDashboard", () => {
  it("renders moderation stats", () => {
    const { container } = render(
      <ContentModDashboard total={100} approved={80} rejected={10} review={10}
        results={[
          { textLength: 50, action: "approve", flagCount: 0 },
          { textLength: 120, action: "reject", flagCount: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Content Moderation");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("80");
    expect(container.textContent).toContain("Approved");
    expect(container.textContent).toContain("Rejected");
  });
});
