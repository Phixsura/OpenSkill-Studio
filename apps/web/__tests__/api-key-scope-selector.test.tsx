import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyScopeSelector } from "@/components/api-key-scope-selector";

describe("ApiKeyScopeSelector", () => {
  const scopes = [
    { scope: "apps:read", label: "Read Apps", category: "apps", risk: "low" },
    { scope: "apps:write", label: "Write Apps", category: "apps", risk: "medium" },
  ];
  it("renders", () => {
    const { container } = render(
      <ApiKeyScopeSelector availableScopes={scopes} selected={new Set(["apps:read"])}
        onToggle={vi.fn()} needsApproval={false} maxRisk="low" />
    );
    expect(container.textContent).toContain("API Key Scopes");
    expect(container.textContent).toContain("1 selected");
    expect(container.textContent).toContain("Read Apps");
    expect(container.textContent).toContain("apps:read");
  });
});
