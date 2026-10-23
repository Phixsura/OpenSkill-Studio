import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SegmentTargetingPreview } from "@/components/segment-targeting-preview";

describe("SegmentTargetingPreview", () => {
  it("renders", () => {
    const { container } = render(
      <SegmentTargetingPreview segments={["new_users", "developers"]}
        matchedContent={["welcome_banner", "sdk_guide"]} totalRules={5} />
    );
    expect(container.textContent).toContain("Segment Targeting");
    expect(container.textContent).toContain("🆕 new users");
    expect(container.textContent).toContain("👨‍💻 developers");
    expect(container.textContent).toContain("2/5");
    expect(container.textContent).toContain("welcome banner");
  });
});
