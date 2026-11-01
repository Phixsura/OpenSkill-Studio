import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SandboxExecutionLog } from "@/components/sandbox-execution-log";

const MOCK_EXECUTIONS = [
  {
    id: "e1",
    app_name: "Image Processor",
    status: "completed" as const,
    started_at: "2026-10-28T14:00:00Z",
    ended_at: "2026-10-28T14:00:02Z",
    duration_ms: 2300,
    resources: { cpu_seconds: 1.8, wall_seconds: 2.3, memory_mb: 64, network_egress_mb: 0.1 },
    exit_code: 0,
    error: null,
    violations: [],
  },
  {
    id: "e2",
    app_name: "Data Cruncher",
    status: "killed" as const,
    started_at: "2026-10-28T13:55:00Z",
    ended_at: "2026-10-28T13:55:35Z",
    duration_ms: 35000,
    resources: { cpu_seconds: 28.5, wall_seconds: 35.0, memory_mb: 480, network_egress_mb: 8.2 },
    exit_code: 137,
    error: "Process killed: CPU time exceeded",
    violations: ["cpu_time: 28.5s > 5.0s", "memory: 480MB > 128MB"],
  },
  {
    id: "e3",
    app_name: "Quick Script",
    status: "running" as const,
    started_at: "2026-10-28T14:01:00Z",
    ended_at: null,
    duration_ms: 500,
    resources: { cpu_seconds: 0.3, wall_seconds: 0.5, memory_mb: 16, network_egress_mb: 0 },
    exit_code: null,
    error: null,
    violations: [],
  },
];

describe("SandboxExecutionLog", () => {
  it("renders heading and counts", () => {
    const { container } = render(
      <SandboxExecutionLog
        executions={MOCK_EXECUTIONS}
        totalCount={42}
        budgetUsed={15}
        budgetLimit={100}
      />,
    );
    expect(container.textContent).toContain("Sandbox Executions");
    expect(container.textContent).toContain("42 total");
    expect(container.textContent).toContain("1 running");
    expect(container.textContent).toContain("1 failed");
  });

  it("renders budget display", () => {
    const { container } = render(
      <SandboxExecutionLog
        executions={MOCK_EXECUTIONS}
        totalCount={3}
        budgetUsed={80}
        budgetLimit={100}
      />,
    );
    expect(container.textContent).toContain("80/100");
  });

  it("renders execution app names", () => {
    const { container } = render(
      <SandboxExecutionLog
        executions={MOCK_EXECUTIONS}
        totalCount={3}
        budgetUsed={3}
        budgetLimit={100}
      />,
    );
    expect(container.textContent).toContain("Image Processor");
    expect(container.textContent).toContain("Data Cruncher");
    expect(container.textContent).toContain("Quick Script");
  });

  it("renders status badges", () => {
    const { container } = render(
      <SandboxExecutionLog
        executions={MOCK_EXECUTIONS}
        totalCount={3}
        budgetUsed={3}
        budgetLimit={100}
      />,
    );
    expect(container.textContent).toContain("Completed");
    expect(container.textContent).toContain("Killed");
    expect(container.textContent).toContain("Running");
  });

  it("renders duration", () => {
    const { container } = render(
      <SandboxExecutionLog
        executions={MOCK_EXECUTIONS}
        totalCount={3}
        budgetUsed={3}
        budgetLimit={100}
      />,
    );
    expect(container.textContent).toContain("2.3s");
    expect(container.textContent).toContain("35.0s");
  });

  it("shows empty state", () => {
    const { container } = render(
      <SandboxExecutionLog executions={[]} totalCount={0} budgetUsed={0} budgetLimit={100} />,
    );
    expect(container.textContent).toContain("No sandbox executions yet");
  });

  it("expands to show resource bars", () => {
    const { container } = render(
      <SandboxExecutionLog
        executions={MOCK_EXECUTIONS}
        totalCount={3}
        budgetUsed={3}
        budgetLimit={100}
      />,
    );
    const buttons = container.querySelectorAll("button[aria-expanded]");
    fireEvent.click(buttons[0]); // expand "Image Processor"
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("Memory");
    expect(container.textContent).toContain("Network");
  });

  it("shows exit code on expand", () => {
    const { container } = render(
      <SandboxExecutionLog
        executions={MOCK_EXECUTIONS}
        totalCount={3}
        budgetUsed={3}
        budgetLimit={100}
      />,
    );
    const buttons = container.querySelectorAll("button[aria-expanded]");
    fireEvent.click(buttons[0]);
    expect(container.textContent).toContain("Exit code:");
    expect(container.textContent).toContain("0");
  });

  it("shows error message on expand", () => {
    const { container } = render(
      <SandboxExecutionLog
        executions={MOCK_EXECUTIONS}
        totalCount={3}
        budgetUsed={3}
        budgetLimit={100}
      />,
    );
    const buttons = container.querySelectorAll("button[aria-expanded]");
    fireEvent.click(buttons[1]); // expand "Data Cruncher"
    expect(container.textContent).toContain("CPU time exceeded");
  });

  it("shows violations on expand", () => {
    const { container } = render(
      <SandboxExecutionLog
        executions={MOCK_EXECUTIONS}
        totalCount={3}
        budgetUsed={3}
        budgetLimit={100}
      />,
    );
    const buttons = container.querySelectorAll("button[aria-expanded]");
    fireEvent.click(buttons[1]);
    expect(container.textContent).toContain("Violations");
    expect(container.textContent).toContain("cpu_time");
    expect(container.textContent).toContain("memory");
  });
});
