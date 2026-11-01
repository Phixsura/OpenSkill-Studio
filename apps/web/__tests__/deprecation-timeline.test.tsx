import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeprecationTimeline } from "@/components/deprecation-timeline";

describe("DeprecationTimeline", () => {
  it("shows days remaining", () => {
    const { container } = render(
      <DeprecationTimeline phase="deprecation" daysRemaining={60} sunsetDate="2027-01-01" />
    );
    expect(container.textContent).toContain("60 days remaining");
  });
  it("shows sunset", () => {
    const { container } = render(
      <DeprecationTimeline phase="sunset" daysRemaining={0} sunsetDate="2026-01-01" />
    );
    expect(container.textContent).toContain("has been sunset");
  });
  it("shows alternative", () => {
    const { container } = render(
      <DeprecationTimeline phase="announced" daysRemaining={120} sunsetDate="2027-06-01" alternativeAppName="NewApp" />
    );
    expect(container.textContent).toContain("NewApp");
  });
});
