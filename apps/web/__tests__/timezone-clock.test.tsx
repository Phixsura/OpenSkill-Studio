import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TimezoneClock } from "@/components/timezone-clock";

describe("TimezoneClock", () => {
  it("renders team times", () => {
    const { container } = render(
      <TimezoneClock fromTz="UTC" fromHour={10} teamTimes={[
        { fromTz: "UTC", toTz: "PST", toHour: 2, display: "02:00 PST", dayChange: "same_day" },
        { fromTz: "UTC", toTz: "JST", toHour: 19, display: "19:00 JST", dayChange: "same_day" },
      ]} />
    );
    expect(container.textContent).toContain("Team Times");
    expect(container.textContent).toContain("10:00 UTC");
    expect(container.textContent).toContain("02:00");
    expect(container.textContent).toContain("PST");
    expect(container.textContent).toContain("19:00");
    expect(container.textContent).toContain("JST");
  });
});
