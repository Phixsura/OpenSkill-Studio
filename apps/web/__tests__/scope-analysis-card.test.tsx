import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScopeAnalysisCard } from "@/components/scope-analysis-card";

const OVER = {
  app_id: "app-1",
  declared_scopes: ["read:skills", "write:projects", "read:email"],
  exercised_scopes: ["read:skills"],
  unused_scopes: ["write:projects", "read:email"],
  undeclared_attempts: [],
  compliance_pct: 33.3,
  over_permissioned: true,
  under_permissioned: false,
  recommendations: ["Remove 2 unused scope(s): read:email, write:projects"],
};

const UNDER = {
  ...OVER,
  unused_scopes: [],
  undeclared_attempts: ["admin:org"],
  compliance_pct: 100,
  over_permissioned: false,
  under_permissioned: true,
  recommendations: ["Add 1 missing scope(s): admin:org"],
};

const PERFECT = {
  ...OVER,
  exercised_scopes: ["read:skills", "write:projects", "read:email"],
  unused_scopes: [],
  undeclared_attempts: [],
  compliance_pct: 100,
  over_permissioned: false,
  under_permissioned: false,
  recommendations: ["All scopes are correctly utilized — no changes needed"],
};

describe("ScopeAnalysisCard", () => {
  it("renders heading and app name", () => {
    const { container } = render(<ScopeAnalysisCard analysis={OVER} appName="My App" />);
    expect(container.textContent).toContain("Scope Analysis");
    expect(container.textContent).toContain("My App");
  });

  it("renders declared count", () => {
    const { container } = render(<ScopeAnalysisCard analysis={OVER} appName="App" />);
    expect(container.textContent).toContain("3 declared");
  });

  it("renders compliance percentage", () => {
    const { container } = render(<ScopeAnalysisCard analysis={OVER} appName="App" />);
    expect(container.textContent).toContain("33.3%");
  });

  it("shows Over-permissioned flag", () => {
    const { container } = render(<ScopeAnalysisCard analysis={OVER} appName="App" />);
    expect(container.textContent).toContain("Over-permissioned");
  });

  it("shows Under-permissioned flag", () => {
    const { container } = render(<ScopeAnalysisCard analysis={UNDER} appName="App" />);
    expect(container.textContent).toContain("Under-permissioned");
  });

  it("shows Correctly scoped flag", () => {
    const { container } = render(<ScopeAnalysisCard analysis={PERFECT} appName="App" />);
    expect(container.textContent).toContain("Correctly scoped");
  });

  it("renders exercised scopes", () => {
    const { container } = render(<ScopeAnalysisCard analysis={OVER} appName="App" />);
    expect(container.textContent).toContain("Exercised");
    expect(container.textContent).toContain("read:skills");
  });

  it("renders unused scopes", () => {
    const { container } = render(<ScopeAnalysisCard analysis={OVER} appName="App" />);
    expect(container.textContent).toContain("Unused");
    expect(container.textContent).toContain("write:projects");
  });

  it("renders denied attempts", () => {
    const { container } = render(<ScopeAnalysisCard analysis={UNDER} appName="App" />);
    expect(container.textContent).toContain("Denied");
    expect(container.textContent).toContain("admin:org");
  });

  it("renders recommendations", () => {
    const { container } = render(<ScopeAnalysisCard analysis={OVER} appName="App" />);
    expect(container.textContent).toContain("Recommendations");
    expect(container.textContent).toContain("Remove 2 unused");
  });

  it("renders perfect recommendation", () => {
    const { container } = render(<ScopeAnalysisCard analysis={PERFECT} appName="App" />);
    expect(container.textContent).toContain("no changes needed");
  });
});
