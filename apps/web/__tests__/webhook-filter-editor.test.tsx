import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookFilterEditor } from "@/components/webhook-filter-editor";

describe("WebhookFilterEditor", () => {
  it("renders filters", () => {
    const { container } = render(
      <WebhookFilterEditor name="prod_only" onAddRule={vi.fn()} onDeleteRule={vi.fn()}
        rules={[
          { name: "env", field: "environment", operator: "eq", value: "production", action: "include" },
          { name: "skip", field: "type", operator: "eq", value: "test", action: "exclude" },
        ]} />
    );
    expect(container.textContent).toContain("Filter: prod_only");
    expect(container.textContent).toContain("2 rules");
    expect(container.textContent).toContain("include");
    expect(container.textContent).toContain("exclude");
    expect(container.textContent).toContain("environment eq production");
  });
});
