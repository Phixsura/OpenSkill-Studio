import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataRetentionPanel } from "@/components/data-retention-panel";

describe("DataRetentionPanel", () => {
  const policies = [
    { type: "logs", description: "App logs", retention: "30 days", autoDelete: true },
    { type: "profiles", description: "User data", retention: "Forever", autoDelete: false },
  ];
  it("renders policies", () => {
    const { container } = render(<DataRetentionPanel policies={policies} autoDeleteCount={1} />);
    expect(container.textContent).toContain("logs");
    expect(container.textContent).toContain("30 days");
    expect(container.textContent).toContain("auto");
    expect(container.textContent).toContain("Forever");
    expect(container.textContent).toContain("1 auto-delete");
  });
});
