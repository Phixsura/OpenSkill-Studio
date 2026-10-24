import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcOwnershipTable } from "@/components/svc-ownership-table";

describe("SvcOwnershipTable", () => {
  it("renders table", () => {
    const { container } = render(
      <SvcOwnershipTable completenessPct={50} complete={1} total={2}
        matrix={[
          { service: "api", team: "platform", oncall: "alice", runbook: true, docs: true },
          { service: "db", team: "data", oncall: "", runbook: false, docs: false },
        ]} />
    );
    expect(container.textContent).toContain("Service Ownership");
    expect(container.textContent).toContain("1/2 complete");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("platform");
    expect(container.textContent).toContain("alice");
  });
});
