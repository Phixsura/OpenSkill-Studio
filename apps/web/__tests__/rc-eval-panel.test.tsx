import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RcEvalPanel } from "@/components/rc-eval-panel";
describe("RcEvalPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RcEvalPanel version="2.0-rc1" verdict="promote" passed={5} total={5}
        checks={{ tests_passing: true, security_scan_clean: true, performance_acceptable: true,
                  error_rate_acceptable: true, code_reviewed: true }} />
    );
    expect(container.textContent).toContain("RC Evaluation: 2.0-rc1");
    expect(container.textContent).toContain("promote");
    expect(container.textContent).toContain("5/5");
    expect(container.textContent).toContain("tests passing");
    expect(container.textContent).toContain("code reviewed");
  });
});
