import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventDedupPanel } from "@/components/event-dedup-panel";
describe("EventDedupPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EventDedupPanel seen={5000} deduped={200} window={10000} />
    );
    expect(container.textContent).toContain("Event Dedup");
    expect(container.textContent).toContain("5000/10000 tracked");
    expect(container.textContent).toContain("200 deduped");
    expect(container.textContent).toContain("5,000"); // from grid toLocaleString
  });
});
