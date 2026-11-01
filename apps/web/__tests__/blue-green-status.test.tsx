import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BlueGreenStatus } from "@/components/blue-green-status";

describe("BlueGreenStatus", () => {
  it("renders", () => {
    const { container } = render(
      <BlueGreenStatus active="blue" slots={{
        blue: { version: "1.0", healthy: true },
        green: { version: "2.0", healthy: false },
      }} />
    );
    expect(container.textContent).toContain("Blue-Green Deploy");
    expect(container.textContent).toContain("active: blue");
    expect(container.textContent).toContain("LIVE");
    expect(container.textContent).toContain("1.0");
    expect(container.textContent).toContain("2.0");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("not ready");
  });
});
