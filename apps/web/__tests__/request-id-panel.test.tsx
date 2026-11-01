import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RequestIdPanel } from "@/components/request-id-panel";
describe("RequestIdPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RequestIdPanel requestId="req_67199abc_deadbeef01234567" prefix="req" traceable={true} valid={true} />
    );
    expect(container.textContent).toContain("Request ID");
    expect(container.textContent).toContain("Valid");
    expect(container.textContent).toContain("prefix: req");
    expect(container.textContent).toContain("req_67199abc_deadbeef01234567");
    expect(container.textContent).toContain("Timestamp embedded");
  });
});
