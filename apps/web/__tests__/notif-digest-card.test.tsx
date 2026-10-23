import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotifDigestCard } from "@/components/notif-digest-card";

describe("NotifDigestCard", () => {
  it("renders digest", () => {
    const { container } = render(
      <NotifDigestCard period="daily" total={4} highPriority={2}
        summary="4 notifications (2 high priority)"
        sections={[
          { category: "alerts", count: 2, items: [
            { title: "Error spike", body: "500 errors", priority: "high" },
          ]},
          { category: "deploys", count: 1, items: [
            { title: "Deploy succeeded", body: "v2.1", priority: "normal" },
          ]},
        ]} />
    );
    expect(container.textContent).toContain("Daily Digest");
    expect(container.textContent).toContain("4 notifications");
    expect(container.textContent).toContain("2 urgent");
    expect(container.textContent).toContain("Error spike");
    expect(container.textContent).toContain("Deploy succeeded");
  });
});
