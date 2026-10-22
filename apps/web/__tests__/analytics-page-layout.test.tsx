import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnalyticsPageLayout } from "@/components/analytics-page-layout";

describe("AnalyticsPageLayout", () => {
  it("shows app name", () => {
    const { container } = render(<AnalyticsPageLayout appName="My App" sections={["installs"]} activeSection="installs" onSectionChange={vi.fn()}><p>Content</p></AnalyticsPageLayout>);
    expect(container.textContent).toContain("My App Analytics");
  });
  it("shows sections", () => {
    const { container } = render(<AnalyticsPageLayout appName="X" sections={["installs", "webhooks"]} activeSection="installs" onSectionChange={vi.fn()}><div /></AnalyticsPageLayout>);
    expect(container.textContent).toContain("installs");
    expect(container.textContent).toContain("webhooks");
  });
});
