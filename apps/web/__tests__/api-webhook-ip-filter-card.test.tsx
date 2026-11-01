import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookIPFilterCard from "../src/components/api-webhook-ip-filter-card";

const rules = [
  { rule_id: "r1", cidr: "10.0.0.0/8", action: "block" as const },
  { rule_id: "r2", cidr: "192.168.0.0/16", action: "allow" as const },
];

describe("APIWebhookIPFilterCard", () => {
  it("renders header and blocked count", () => {
    const { container } = render(<APIWebhookIPFilterCard rules={rules} blockedCount={5} appName="App" />);
    expect(container.textContent).toContain("Webhook IP Filter");
    expect(container.textContent).toContain("5 blocked");
  });

  it("shows CIDRs and actions", () => {
    const { container } = render(<APIWebhookIPFilterCard rules={rules} blockedCount={0} appName="App" />);
    expect(container.textContent).toContain("10.0.0.0/8");
    expect(container.textContent).toContain("block");
    expect(container.textContent).toContain("allow");
  });

  it("shows empty state", () => {
    const { container } = render(<APIWebhookIPFilterCard rules={[]} blockedCount={0} appName="App" />);
    expect(container.textContent).toContain("No IP filter rules");
  });
});
