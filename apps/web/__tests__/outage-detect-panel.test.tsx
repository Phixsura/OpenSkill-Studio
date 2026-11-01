import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OutageDetectPanel } from "@/components/outage-detect-panel";

describe("OutageDetectPanel", () => {
  it("renders outage", () => {
    const { container } = render(
      <OutageDetectPanel outage={true} classification="partial"
        affectedServices={["db", "cache"]} downCount={1} degradedCount={1} />
    );
    expect(container.textContent).toContain("PARTIAL OUTAGE");
    expect(container.textContent).toContain("1 down");
    expect(container.textContent).toContain("1 degraded");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("cache");
  });
  it("renders healthy", () => {
    const { container } = render(
      <OutageDetectPanel outage={false} classification="none"
        affectedServices={[]} downCount={0} degradedCount={0} />
    );
    expect(container.textContent).toContain("All Systems Operational");
  });
});
