import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperChangelogWidgetCard from "../src/components/api-developer-changelog-widget-card";

const widget = { position: "bottom-right", trigger: "bell", max_items: 5, theme: "auto", impressions: 1000, clicks: 50, ctr: 5.0 };

describe("APIDeveloperChangelogWidgetCard", () => {
  it("shows config and stats", () => {
    const { container } = render(<APIDeveloperChangelogWidgetCard widget={widget} appName="App" />);
    expect(container.textContent).toContain("Changelog Widget");
    expect(container.textContent).toContain("bottom-right");
    expect(container.textContent).toContain("bell");
    expect(container.textContent).toContain("5% CTR");
  });
  it("shows not configured", () => {
    const { container } = render(<APIDeveloperChangelogWidgetCard widget={null} appName="App" />);
    expect(container.textContent).toContain("Widget not configured");
  });
});
