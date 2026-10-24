import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TrafficPolicyEditor } from "@/components/traffic-policy-editor";

describe("TrafficPolicyEditor", () => {
  it("renders rules", () => {
    const { container } = render(
      <TrafficPolicyEditor name="API Policy" onAddRule={vi.fn()} onDeleteRule={vi.fn()}
        rules={[
          { match: "/api/admin/*", action: "deny", priority: 1, rateLimit: 0, timeoutMs: 5000 },
          { match: "/*", action: "allow", priority: 100, rateLimit: 60, timeoutMs: 30000 },
        ]} />
    );
    expect(container.textContent).toContain("API Policy");
    expect(container.textContent).toContain("2 rules");
    expect(container.textContent).toContain("/api/admin/*");
    expect(container.textContent).toContain("deny");
    expect(container.textContent).toContain("allow");
    expect(container.textContent).toContain("60 rpm");
  });
});
