import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FlagEvalDebugger } from "@/components/flag-eval-debugger";

describe("FlagEvalDebugger", () => {
  it("renders evaluations", () => {
    const { container } = render(
      <FlagEvalDebugger userId="u1" results={[
        { flag: "new_ui", enabled: true, matchedRule: "beta_users", reason: "rule_match" },
        { flag: "dark_mode", enabled: false, reason: "default" },
      ]} />
    );
    expect(container.textContent).toContain("Flag Evaluation");
    expect(container.textContent).toContain("user: u1");
    expect(container.textContent).toContain("1/2 on");
    expect(container.textContent).toContain("new_ui");
    expect(container.textContent).toContain("beta_users");
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("default");
  });
});
