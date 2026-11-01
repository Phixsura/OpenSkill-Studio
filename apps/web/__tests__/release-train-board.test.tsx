import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseTrainBoard } from "@/components/release-train-board";

describe("ReleaseTrainBoard", () => {
  it("renders train", () => {
    const { container } = render(
      <ReleaseTrainBoard name="Q4 Release" targetDate="2024-12-15" pctReady={33} allReady={false}
        services={[
          { service: "api", version: "3.0", status: "ready", owner: "alice" },
          { service: "web", version: "3.0", status: "pending", owner: "bob" },
          { service: "worker", version: "3.0", status: "blocked", owner: "carol" },
        ]} />
    );
    expect(container.textContent).toContain("Q4 Release");
    expect(container.textContent).toContain("2024-12-15");
    expect(container.textContent).toContain("33%");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("ready");
    expect(container.textContent).toContain("blocked");
  });
});
