import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TimezoneClockStrip } from "@/components/timezone-clock-strip";

describe("TimezoneClockStrip", () => {
  const times = [
    { timezone: "UTC", offset: 0, time: "12:00", date: "2026-10-23" },
    { timezone: "US/Pacific", offset: -8, time: "04:00", date: "2026-10-23" },
    { timezone: "Asia/Tokyo", offset: 9, time: "21:00", date: "2026-10-23" },
  ];
  it("renders", () => {
    const { container } = render(<TimezoneClockStrip times={times} />);
    expect(container.textContent).toContain("12:00");
    expect(container.textContent).toContain("UTC");
    expect(container.textContent).toContain("04:00");
    expect(container.textContent).toContain("PST");
    expect(container.textContent).toContain("21:00");
    expect(container.textContent).toContain("JST");
  });
});
