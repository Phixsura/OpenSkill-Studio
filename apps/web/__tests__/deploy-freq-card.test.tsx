import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployFreqCard } from "@/components/deploy-freq-card";

describe("DeployFreqCard", () => {
  it("renders", () => {
    const { container } = render(
      <DeployFreqCard frequency="on_demand" deploysPerDay={2} total={60}
        periodDays={30} byEnv={{ prod: 40, staging: 20 }} />
    );
    expect(container.textContent).toContain("Deploy Frequency");
    expect(container.textContent).toContain("on_demand");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("30d");
    expect(container.textContent).toContain("prod: 40");
  });
});
