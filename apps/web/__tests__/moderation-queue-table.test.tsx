import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ModerationQueueTable } from "@/components/moderation-queue-table";

describe("ModerationQueueTable", () => {
  it("renders queue", () => {
    const { container } = render(
      <ModerationQueueTable
        items={[
          { id: "c1", status: "approved", flags: [], safeText: "Great app!" },
          { id: "c2", status: "rejected", flags: ["blocked_word"], safeText: "spam content" },
        ]}
        counts={{ approved: 1, flagged: 0, rejected: 1 }}
        queueHealth="needs_review" />
    );
    expect(container.textContent).toContain("Moderation Queue");
    expect(container.textContent).toContain("Needs Review");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("approved");
    expect(container.textContent).toContain("rejected");
    expect(container.textContent).toContain("blocked_word");
  });
});
