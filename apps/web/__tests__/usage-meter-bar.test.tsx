import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageMeterBar } from "@/components/usage-meter-bar";

describe("UsageMeterBar", () => {
  it("renders meters", () => {
    const { container } = render(
      <UsageMeterBar meters={[
        { label: "API Calls", pct: 90, status: "critical", display: "45,000 / 50,000", remainingDisplay: "5,000" },
        { label: "Storage", pct: 20, status: "ok", display: "2,000 / 10,000 MB", remainingDisplay: "8,000 MB" },
      ]} />
    );
    expect(container.textContent).toContain("Usage");
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("45,000 / 50,000");
    expect(container.textContent).toContain("5,000 remaining");
    expect(container.textContent).toContain("Storage");
  });
});
