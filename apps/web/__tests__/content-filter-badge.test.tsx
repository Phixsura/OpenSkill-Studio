import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContentFilterBadge } from "@/components/content-filter-badge";

describe("ContentFilterBadge", () => {
  it("renders safe", () => {
    const { container } = render(<ContentFilterBadge safe={true} maxSeverity="none" flagCount={0} flags={[]} />);
    expect(container.textContent).toContain("Safe");
  });
  it("renders flagged", () => {
    const flags = [{ word: "spam", severity: "high" }, { word: "phishing", severity: "critical" }];
    const { container } = render(<ContentFilterBadge safe={false} maxSeverity="critical" flagCount={2} flags={flags} />);
    expect(container.textContent).toContain("2 issues");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("spam");
    expect(container.textContent).toContain("phishing");
  });
});
