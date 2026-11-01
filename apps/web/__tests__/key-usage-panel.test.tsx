import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { KeyUsagePanel } from "@/components/key-usage-panel";
describe("KeyUsagePanel", () => {
  it("renders", () => {
    const { container } = render(
      <KeyUsagePanel totalKeys={2} totalRequests={5000}
        keys={[
          { keyPreview: "key_abc1...", requests: 3000, uniqueEndpoints: 5, errorRate: 2 },
          { keyPreview: "key_xyz7...", requests: 2000, uniqueEndpoints: 3, errorRate: 0.5 },
        ]} />
    );
    expect(container.textContent).toContain("Key Usage Analytics");
    expect(container.textContent).toContain("2 keys");
    expect(container.textContent).toContain("5,000 reqs");
    expect(container.textContent).toContain("key_abc1...");
    expect(container.textContent).toContain("3,000 reqs");
    expect(container.textContent).toContain("5 eps");
  });
});
