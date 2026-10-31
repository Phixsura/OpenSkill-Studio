import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PriorityRouterPanel } from "@/components/priority-router-panel";

describe("PriorityRouterPanel", () => {
  it("renders", () => {
    const { container } = render(
      <PriorityRouterPanel totalQueued={15} processed={5000}
        depths={{ critical: 2, high: 3, normal: 5, low: 3, background: 2 }} />
    );
    expect(container.textContent).toContain("Priority Router");
    expect(container.textContent).toContain("15 queued");
    expect(container.textContent).toContain("5,000 processed");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("normal");
  });
});
