import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WhEventFilterPanel } from "@/components/wh-event-filter-panel";
describe("WhEventFilterPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WhEventFilterPanel filters={[
        { subscriberId: "sub-1", eventCount: 3, hasFieldFilter: true },
        { subscriberId: "sub-2", eventCount: 1, hasFieldFilter: false },
      ]} />
    );
    expect(container.textContent).toContain("Event Filters");
    expect(container.textContent).toContain("2 subscribers filtered");
    expect(container.textContent).toContain("sub-1");
    expect(container.textContent).toContain("3 events");
    expect(container.textContent).toContain("field filter");
  });
});
