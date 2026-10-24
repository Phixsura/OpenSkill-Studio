import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetPolicyAnalyzer } from "@/components/net-policy-analyzer";

describe("NetPolicyAnalyzer", () => {
  it("renders", () => {
    const { container } = render(
      <NetPolicyAnalyzer total={10} allow={7} deny={3}
        overlyPermissive={["bad-rule"]} securityScore={80} />
    );
    expect(container.textContent).toContain("Network Policy Audit");
    expect(container.textContent).toContain("10 policies");
    expect(container.textContent).toContain("score: 80/100");
    expect(container.textContent).toContain("7");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("bad-rule");
  });
});
