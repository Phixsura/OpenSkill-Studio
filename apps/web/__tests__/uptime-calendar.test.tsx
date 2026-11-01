import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UptimeCalendar } from "@/components/uptime-calendar";

describe("UptimeCalendar", () => {
  it("renders calendar", () => {
    const days = [
      { date: "2026-01-01", uptime_pct: 100, status: "good" },
      { date: "2026-01-02", uptime_pct: 98, status: "outage" },
    ];
    const { container } = render(<UptimeCalendar days={days} uptimePct={99.5} period="30d" />);
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("30d");
    expect(container.textContent).toContain("2 days");
  });
});
