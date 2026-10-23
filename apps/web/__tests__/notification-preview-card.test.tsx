import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotificationPreviewCard } from "@/components/notification-preview-card";

describe("NotificationPreviewCard", () => {
  it("renders preview", () => {
    const { container } = render(
      <NotificationPreviewCard emoji="🚨" title="High CPU" message="CPU at 95%"
        color="#DC2626" service="api" channel="alerts" />
    );
    expect(container.textContent).toContain("High CPU");
    expect(container.textContent).toContain("CPU at 95%");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("#alerts");
  });
});
