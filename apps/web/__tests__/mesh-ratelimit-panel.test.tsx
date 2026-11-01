import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshRatelimitPanel } from "@/components/mesh-ratelimit-panel";
describe("MeshRatelimitPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshRatelimitPanel limits={[
        { key: "web→api", rpm: 100, currentCount: 50 },
        { key: "api→db", rpm: 500, currentCount: 499 },
      ]} />
    );
    expect(container.textContent).toContain("Mesh Rate Limits");
    expect(container.textContent).toContain("2 limits");
    expect(container.textContent).toContain("50/100 rpm");
    expect(container.textContent).toContain("499/500 rpm");
  });
});
