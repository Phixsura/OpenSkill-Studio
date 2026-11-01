import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformFinalStatus } from "@/components/platform-final-status";

describe("PlatformFinalStatus", () => {
  it("renders status", () => {
    const { container } = render(
      <PlatformFinalStatus milestone="211,000 LINES" commits={2431} lines={211000}
        files={7062} modules={10} milestones={["200K crossed", "7K files"]} />
    );
    expect(container.textContent).toContain("211,000 LINES");
    expect(container.textContent).toContain("2,431");
    expect(container.textContent).toContain("7,062");
    expect(container.textContent).toContain("200K crossed");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
  });
});
