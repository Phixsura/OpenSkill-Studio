import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LogRetentionPanel } from "@/components/log-retention-panel";

describe("LogRetentionPanel", () => {
  it("renders actions", () => {
    const { container } = render(
      <LogRetentionPanel totalReclaimableGb={33.3} onPurge={vi.fn()}
        actions={[
          { source: "api-logs", policy: "default", reclaimableGb: 33.3, daysOver: 60 },
        ]} />
    );
    expect(container.textContent).toContain("Log Retention");
    expect(container.textContent).toContain("33.3 GB reclaimable");
    expect(container.textContent).toContain("api-logs");
    expect(container.textContent).toContain("60d over");
    expect(container.textContent).toContain("Purge");
  });
});
