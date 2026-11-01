import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HttpClientPanel } from "@/components/http-client-panel";

const mockLogs = [
  { requestId: "r1", method: "GET", url: "https://api.example.com/data",
    statusCode: 200, latencyMs: 45, blocked: false },
  { requestId: "r2", method: "POST", url: "http://127.0.0.1/admin",
    statusCode: 0, latencyMs: 0, blocked: true, blockReason: "Private host" },
];
const mockAllowlist = [{ pattern: "https://api.example.com/*" }];

describe("HttpClientPanel", () => {
  it("renders request logs", () => {
    const { container } = render(
      <HttpClientPanel logs={mockLogs} allowlist={mockAllowlist} blockedCount={1} />
    );
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("1 blocked");
  });

  it("shows blocked reason", () => {
    const { container } = render(
      <HttpClientPanel logs={mockLogs} allowlist={mockAllowlist} blockedCount={1} />
    );
    expect(container.textContent).toContain("Private host");
  });

  it("shows allowlist tab", () => {
    const { getByText, container } = render(
      <HttpClientPanel logs={mockLogs} allowlist={mockAllowlist} blockedCount={0} />
    );
    fireEvent.click(getByText("Allowlist (1)"));
    expect(container.textContent).toContain("https://api.example.com/*");
  });

  it("calls onAddPattern", () => {
    const onAdd = vi.fn();
    const { getByText, getByPlaceholderText } = render(
      <HttpClientPanel logs={[]} allowlist={[]} blockedCount={0} onAddPattern={onAdd} />
    );
    fireEvent.click(getByText("Allowlist (0)"));
    fireEvent.change(getByPlaceholderText("https://api.example.com/*"), { target: { value: "https://new.com/*" } });
    fireEvent.click(getByText("Add"));
    expect(onAdd).toHaveBeenCalledWith("https://new.com/*");
  });
});
