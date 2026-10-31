import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-api-consumer-api-token-scope-audit-card";

describe("TokenScopeAuditCard", () => {
  it("shows audit data", () => {
    const { container } = render(<Card consumerId="c1" totalChecks={100} grantedCount={90} deniedCount={10} uniqueScopes={5} mostUsed="read:users" mostDenied="write:admin" unusedScopes={["delete:all"]} appName="App" />);
    expect(container.textContent).toContain("Scope Audit");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("read:users");
    expect(container.textContent).toContain("write:admin");
    expect(container.textContent).toContain("delete:all");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumerId="c1" totalChecks={0} grantedCount={0} deniedCount={0} uniqueScopes={0} mostUsed="" mostDenied="" unusedScopes={[]} appName="App" />);
    expect(container.textContent).toContain("Scope Audit");
  });
});
