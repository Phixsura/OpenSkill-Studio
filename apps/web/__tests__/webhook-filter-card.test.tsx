import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookFilterCard from "../src/components/webhook-filter-card";

const filters = [
  {
    filter_id: "f1",
    webhook_id: "wh-1",
    patterns: ["user.*", "order.*"],
    mode: "include" as const,
  },
  { filter_id: "f2", webhook_id: "wh-1", patterns: ["internal.*"], mode: "exclude" as const },
];

describe("WebhookFilterCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<WebhookFilterCard filters={filters} appName="My App" />);
    expect(container.textContent).toContain("Webhook Filters");
    expect(container.textContent).toContain("My App");
  });

  it("shows include/exclude counts", () => {
    const { container } = render(<WebhookFilterCard filters={filters} appName="App" />);
    expect(container.textContent).toContain("1 include");
    expect(container.textContent).toContain("1 exclude");
  });

  it("renders patterns", () => {
    const { container } = render(<WebhookFilterCard filters={filters} appName="App" />);
    expect(container.textContent).toContain("user.*");
    expect(container.textContent).toContain("order.*");
    expect(container.textContent).toContain("internal.*");
  });

  it("shows webhook id", () => {
    const { container } = render(<WebhookFilterCard filters={filters} appName="App" />);
    expect(container.textContent).toContain("wh-1");
  });

  it("shows mode labels", () => {
    const { container } = render(<WebhookFilterCard filters={filters} appName="App" />);
    expect(container.textContent).toContain("include");
    expect(container.textContent).toContain("exclude");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookFilterCard filters={[]} appName="App" />);
    expect(container.textContent).toContain("all events delivered");
  });
});
