import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PermissionsOverview } from "@/components/permissions-overview";

describe("PermissionsOverview", () => {
  it("shows grouped permissions", () => {
    const { container } = render(<PermissionsOverview read={["read:cohorts"]} write={["write:projects"]} special={["subscribe:events"]} total={3} />);
    expect(container.textContent).toContain("read:cohorts");
    expect(container.textContent).toContain("write:projects");
    expect(container.textContent).toContain("subscribe:events");
    expect(container.textContent).toContain("(3)");
  });
});
