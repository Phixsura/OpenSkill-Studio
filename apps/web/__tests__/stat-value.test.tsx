import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatValue } from "@/components/stat-value";

describe("StatValue", () => {
  it("renders value", () => {
    const { container } = render(<StatValue value={5000} label="Installs" icon="📥" />);
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("Installs");
    expect(container.textContent).toContain("📥");
  });
  it("shows trend", () => {
    const { container } = render(<StatValue value="$1,000" label="MRR" trend={{ direction: "up", pct: 15 }} />);
    expect(container.textContent).toContain("↑");
    expect(container.textContent).toContain("15%");
  });
  it("string value", () => {
    const { container } = render(<StatValue value="99.9%" label="Uptime" />);
    expect(container.textContent).toContain("99.9%");
  });
});
