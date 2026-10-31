import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UserActivityFeed } from "@/components/user-activity-feed";

describe("UserActivityFeed", () => {
  it("renders feed", () => {
    const { container } = render(
      <UserActivityFeed userName="alice" entries={[
        { action: "deploy", resource: "app/myapp", details: "v2.1", timestamp: 1 },
        { action: "create", resource: "app/myapp", details: "", timestamp: 0 },
      ]} />
    );
    expect(container.textContent).toContain("Activity");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("deploy");
    expect(container.textContent).toContain("app/myapp");
    expect(container.textContent).toContain("v2.1");
  });
});
