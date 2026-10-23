import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RealtimeCounterDisplay } from "@/components/realtime-counter";

describe("RealtimeCounterDisplay", () => {
  const counters = [
    { key: "views", count: 1500 },
    { key: "clicks", count: 320 },
    { key: "signups", count: 45 },
  ];
  it("renders counters and total", () => {
    const { container } = render(<RealtimeCounterDisplay counters={counters} grandTotal={1865} />);
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("views");
    expect(container.textContent).toContain("clicks");
    expect(container.textContent).toContain("1,865");
  });
});
