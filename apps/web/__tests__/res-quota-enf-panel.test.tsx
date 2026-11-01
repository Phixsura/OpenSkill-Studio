import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResQuotaEnfPanel } from "@/components/res-quota-enf-panel";
describe("ResQuotaEnfPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ResQuotaEnfPanel quotas={[
        { namespace: "prod", resource: "cpu", used: 8, limit: 10, pct: 80 },
        { namespace: "staging", resource: "memory", used: 2, limit: 8, pct: 25 },
      ]} />
    );
    expect(container.textContent).toContain("Resource Quotas");
    expect(container.textContent).toContain("prod/cpu");
    expect(container.textContent).toContain("8/10");
    expect(container.textContent).toContain("80%");
  });
});
