import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RequestDebuggerCard from "../src/components/api-developer-platform-sdk-consumer-api-request-debugger-card";

describe("RequestDebuggerCard", () => {
  it("renders title and traces", () => {
    const { container } = render(<RequestDebuggerCard />);
    expect(container.textContent).toContain("Request Debugger");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("/api/orders");
  });

  it("shows trace count and errors", () => {
    const { container } = render(<RequestDebuggerCard />);
    expect(container.textContent).toContain("3 traces");
    expect(container.textContent).toContain("1 errors");
  });
});
