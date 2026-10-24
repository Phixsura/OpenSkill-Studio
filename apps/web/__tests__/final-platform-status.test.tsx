import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FinalPlatformStatus } from "@/components/final-platform-status";

describe("FinalPlatformStatus", () => {
  it("renders", () => {
    const { container } = render(
      <FinalPlatformStatus grade="A" score={98} commits={2756} lines={237500}
        files={8118} modules={10} uptime={99.99} nps={55} />
    );
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("98/100");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
    expect(container.textContent).toContain("2,756");
    expect(container.textContent).toContain("238K");
    expect(container.textContent).toContain("8,118");
    expect(container.textContent).toContain("10");
  });
});
