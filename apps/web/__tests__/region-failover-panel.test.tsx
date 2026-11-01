import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RegionFailoverPanel } from "@/components/region-failover-panel";
describe("RegionFailoverPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RegionFailoverPanel primary="eu-west" failed={["us-east"]}
        regions={[
          { name: "us-east", status: "failed", isPrimary: false },
          { name: "eu-west", status: "active", isPrimary: true },
          { name: "ap-south", status: "active", isPrimary: false },
        ]} />
    );
    expect(container.textContent).toContain("Region Failover");
    expect(container.textContent).toContain("primary: eu-west");
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("us-east");
    expect(container.textContent).toContain("failed");
    expect(container.textContent).toContain("PRIMARY");
  });
});
