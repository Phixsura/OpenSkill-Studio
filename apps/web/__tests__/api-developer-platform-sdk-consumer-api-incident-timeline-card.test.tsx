import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IncidentTimelineCard from "../src/components/api-developer-platform-sdk-consumer-api-incident-timeline-card";

describe("IncidentTimelineCard", () => {
  it("renders title and events", () => {
    const { container } = render(<IncidentTimelineCard />);
    expect(container.textContent).toContain("Incident Timeline");
    expect(container.textContent).toContain("Payment API Timeout");
    expect(container.textContent).toContain("detected");
    expect(container.textContent).toContain("identified");
  });

  it("shows severity and event count", () => {
    const { container } = render(<IncidentTimelineCard />);
    expect(container.textContent).toContain("p1");
    expect(container.textContent).toContain("3 events");
  });
});
