import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatCounterDisplay } from "@/components/stat-counter-display";

describe("StatCounterDisplay", () => {
  it("renders counters", () => {
    const { container } = render(
      <StatCounterDisplay total={112} counters={[
        { key: "page_views", value: 12 },
        { key: "api_calls", value: 100 },
      ]} />
    );
    expect(container.textContent).toContain("Counters");
    expect(container.textContent).toContain("112");
    expect(container.textContent).toContain("page views");
    expect(container.textContent).toContain("100");
  });
});
