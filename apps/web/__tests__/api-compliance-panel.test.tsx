import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiCompliancePanel } from "@/components/api-compliance-panel";
describe("ApiCompliancePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ApiCompliancePanel compliancePct={50} total={2}
        results={[
          { endpoint: "/api/v1/users", compliant: true, issueCount: 0 },
          { endpoint: "/legacy", compliant: false, issueCount: 2 },
        ]} />
    );
    expect(container.textContent).toContain("API Compliance");
    expect(container.textContent).toContain("50% compliant");
    expect(container.textContent).toContain("2 endpoints");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("/legacy");
    expect(container.textContent).toContain("2 issues");
  });
});
