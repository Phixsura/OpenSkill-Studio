import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OpsCenter } from "@/components/ops-center";

describe("OpsCenter", () => {
  it("renders center", () => {
    const { container } = render(
      <OpsCenter overallScore={97.5} status="green"
        dimensions={{ services: 100, infrastructure: 99.99, security: 100, deployments: 98 }}
        actionItems={[]} />
    );
    expect(container.textContent).toContain("97.5");
    expect(container.textContent).toContain("Platform Operations Score");
    expect(container.textContent).toContain("services");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("98%");
  });
});
