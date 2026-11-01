import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Platform234kStatus } from "@/components/platform-234k-status";

describe("Platform234kStatus", () => {
  it("renders", () => {
    const { container } = render(<Platform234kStatus />);
    expect(container.textContent).toContain("234K+");
    expect(container.textContent).toContain("All Systems Go");
  });
});
