import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiSandboxConsole } from "@/components/api-sandbox-console";

const history = [
  { requestId: "r1", method: "GET", path: "/api/users", responseCode: 200, responseBody: "{}", latencyMs: 5.2 },
  { requestId: "r2", method: "POST", path: "/api/data", responseCode: 500, responseBody: "{}", latencyMs: 12.1 },
];

describe("ApiSandboxConsole", () => {
  it("renders console", () => {
    const { container } = render(<ApiSandboxConsole history={history} />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
  it("execute request", () => {
    const fn = vi.fn();
    const { container } = render(<ApiSandboxConsole history={[]} onExecute={fn} />);
    const sendBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Send");
    if (sendBtn) fireEvent.click(sendBtn);
    expect(fn).toHaveBeenCalled();
  });
});
