import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookIPAllowlistCard from "../src/components/api-developer-api-webhook-ip-allowlist-card";

const allowlists = [
  { allowlist_id: "production", entries: ["10.0.0.0/8", "192.168.1.0/24"], allowed_count: 500, blocked_count: 15 },
];

describe("APIDeveloperAPIWebhookIPAllowlistCard", () => {
  it("shows allowlists", () => {
    const { container } = render(<APIDeveloperAPIWebhookIPAllowlistCard allowlists={allowlists} appName="App" />);
    expect(container.textContent).toContain("IP Allowlist");
    expect(container.textContent).toContain("15 blocked");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("2 entries");
    expect(container.textContent).toContain("500 allowed");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookIPAllowlistCard allowlists={[]} appName="App" />);
    expect(container.textContent).toContain("No allowlists");
  });
});
