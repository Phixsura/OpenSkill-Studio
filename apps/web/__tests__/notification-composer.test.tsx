import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotificationComposer } from "@/components/notification-composer";

describe("NotificationComposer", () => {
  it("renders notification", () => {
    const { container } = render(
      <NotificationComposer title="Deploy Complete" body="v2.1 deployed"
        icon="🚀" priority="high" channels={["in_app", "email", "slack"]}
        actionUrl="/deploys/123" />
    );
    expect(container.textContent).toContain("Deploy Complete");
    expect(container.textContent).toContain("v2.1 deployed");
    expect(container.textContent).toContain("high");
    expect(container.textContent).toContain("in_app");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("View →");
  });
});
