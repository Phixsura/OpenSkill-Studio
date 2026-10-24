import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqPriorityPanel } from "@/components/req-priority-panel";
describe("ReqPriorityPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqPriorityPanel total={1000}
        byPriority={{ critical: 50, high: 200, normal: 700, low: 50 }} />
    );
    expect(container.textContent).toContain("Request Priority");
    expect(container.textContent).toContain("1,000 classified");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("normal");
    expect(container.textContent).toContain("700");
  });
});
