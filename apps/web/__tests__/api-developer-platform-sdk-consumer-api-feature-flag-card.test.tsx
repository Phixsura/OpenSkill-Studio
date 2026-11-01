import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import FeatureFlagCard from "../src/components/api-developer-platform-sdk-consumer-api-feature-flag-card";

describe("FeatureFlagCard", () => {
  it("renders title and flags", () => {
    const { container } = render(<FeatureFlagCard />);
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("New Dashboard");
    expect(container.textContent).toContain("V2 Search");
    expect(container.textContent).toContain("Beta Analytics");
  });

  it("shows rollout and active count", () => {
    const { container } = render(<FeatureFlagCard />);
    expect(container.textContent).toContain("25% rollout");
    expect(container.textContent).toContain("disabled");
    expect(container.textContent).toContain("2/3 flags active");
  });
});
