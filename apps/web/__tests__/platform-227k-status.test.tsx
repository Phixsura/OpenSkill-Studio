import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Platform227kStatus } from "@/components/platform-227k-status";

describe("Platform227kStatus", () => {
  it("renders", () => {
    const { container } = render(<Platform227kStatus />);
    expect(container.textContent).toContain("227K+");
    expect(container.textContent).toContain("2,640+");
    expect(container.textContent).toContain("7,680+");
    expect(container.textContent).toContain("All Systems Go");
  });
});
