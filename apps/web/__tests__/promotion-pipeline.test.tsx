import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PromotionPipeline } from "@/components/promotion-pipeline";

describe("PromotionPipeline", () => {
  it("renders pipeline", () => {
    const { container } = render(
      <PromotionPipeline version="3.0" currentEnv="development" onPromote={vi.fn()}
        pipeline={[
          { environment: "development", status: "deployed", requiresApproval: false },
          { environment: "staging", status: "pending", requiresApproval: false },
          { environment: "production", status: "pending", requiresApproval: true },
        ]} />
    );
    expect(container.textContent).toContain("Promotion: v3.0");
    expect(container.textContent).toContain("development");
    expect(container.textContent).toContain("deployed");
    expect(container.textContent).toContain("staging");
    expect(container.textContent).toContain("Promote");
    expect(container.textContent).toContain("Approve");
  });
});
