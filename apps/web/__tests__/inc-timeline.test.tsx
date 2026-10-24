import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncTimeline } from "@/components/inc-timeline";

describe("IncTimeline", () => {
  it("renders timeline", () => {
    const { container } = render(
      <IncTimeline durationMin={10} eventCount={3} events={[
        { type: "alert", message: "CPU spike detected" },
        { type: "ack" },
        { type: "resolved", message: "Fixed" },
      ]} />
    );
    expect(container.textContent).toContain("Incident Timeline");
    expect(container.textContent).toContain("3 events");
    expect(container.textContent).toContain("10min");
    expect(container.textContent).toContain("alert");
    expect(container.textContent).toContain("resolved");
  });
});
