import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppDetailTabs } from "@/components/app-detail-tabs";

describe("AppDetailTabs", () => {
  it("shows base tabs", () => {
    const { container } = render(<AppDetailTabs activeTab="overview" onTabChange={vi.fn()} hasWebhooks={false} hasSandbox={false} />);
    expect(container.textContent).toContain("Overview");
    expect(container.textContent).toContain("Versions");
  });
  it("shows webhook tab", () => {
    const { container } = render(<AppDetailTabs activeTab="overview" onTabChange={vi.fn()} hasWebhooks={true} hasSandbox={false} />);
    expect(container.textContent).toContain("Webhooks");
  });
  it("shows sandbox tab", () => {
    const { container } = render(<AppDetailTabs activeTab="overview" onTabChange={vi.fn()} hasWebhooks={false} hasSandbox={true} />);
    expect(container.textContent).toContain("Sandbox");
  });
});
