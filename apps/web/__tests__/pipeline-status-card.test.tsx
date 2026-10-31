import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PipelineStatusCard } from "@/components/pipeline-status-card";

describe("PipelineStatusCard", () => {
  it("renders pipeline", () => {
    const { container } = render(
      <PipelineStatusCard name="Data Sync" status="running" transformCount={3} successRate={95} lastRunAt="2026-06-01T10:00:00Z" />
    );
    expect(container.textContent).toContain("Data Sync");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("3");
  });
});
