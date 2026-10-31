import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformProgressBar } from "@/components/platform-progress-bar";

describe("PlatformProgressBar", () => {
  it("renders", () => {
    const { container } = render(
      <PlatformProgressBar commits={1560} lines={138000} files={4171}
        services={930} components={830} target="140K lines" />
    );
    expect(container.textContent).toContain("Platform Progress");
    expect(container.textContent).toContain("1,560");
    expect(container.textContent).toContain("138,000");
    expect(container.textContent).toContain("4,171");
    expect(container.textContent).toContain("Target: 140K lines");
  });
});
