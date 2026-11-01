import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TimelineChart } from "@/components/timeline-chart";

const DATA = [{ date: "Jan 1", value: 10 }, { date: "Jan 2", value: 20 }, { date: "Jan 3", value: 15 }];

describe("TimelineChart", () => {
  it("shows label", () => {
    const { container } = render(<TimelineChart data={DATA} label="API Calls" />);
    expect(container.textContent).toContain("API Calls");
  });

  it("shows date range", () => {
    const { container } = render(<TimelineChart data={DATA} label="X" />);
    expect(container.textContent).toContain("Jan 1");
    expect(container.textContent).toContain("Jan 3");
  });

  it("empty state", () => {
    const { container } = render(<TimelineChart data={[]} label="X" />);
    expect(container.textContent).toContain("No data");
  });
});
