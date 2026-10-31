import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformHealthIndicator } from "@/components/platform-health-indicator";

describe("PlatformHealthIndicator", () => {
  it("shows healthy", () => {
    const { container } = render(<PlatformHealthIndicator health="healthy" errorRate={1.5} pendingReviews={2} />);
    expect(container.textContent).toContain("operational");
    expect(container.textContent).toContain("💚");
  });

  it("shows degraded", () => {
    const { container } = render(<PlatformHealthIndicator health="degraded" errorRate={10} pendingReviews={0} />);
    expect(container.textContent).toContain("issues detected");
  });

  it("shows critical", () => {
    const { container } = render(<PlatformHealthIndicator health="critical" errorRate={25} pendingReviews={5} />);
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("🚨");
  });

  it("shows stats", () => {
    const { container } = render(<PlatformHealthIndicator health="healthy" errorRate={2.5} pendingReviews={3} />);
    expect(container.textContent).toContain("2.5%");
    expect(container.textContent).toContain("3 pending");
  });
});
