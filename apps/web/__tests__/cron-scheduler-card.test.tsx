import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CronSchedulerCard from "../src/components/cron-scheduler-card";

const enabledTask = {
  task_id: "t1",
  name: "Sync Data",
  schedule: "every 5 min",
  status: "enabled" as const,
  run_count: 42,
  last_run_at: new Date(Date.now() - 300_000).toISOString(),
  next_run_at: new Date(Date.now() + 300_000).toISOString(),
  last_error: null,
};

const failedTask = {
  task_id: "t2",
  name: "Send Reports",
  schedule: "daily at 9am",
  status: "enabled" as const,
  run_count: 10,
  last_run_at: new Date(Date.now() - 86_400_000).toISOString(),
  next_run_at: new Date(Date.now() + 43_200_000).toISOString(),
  last_error: "SMTP timeout",
};

const disabledTask = {
  task_id: "t3",
  name: "Archive Logs",
  schedule: "weekly",
  status: "disabled" as const,
  run_count: 5,
  last_run_at: null,
  next_run_at: null,
  last_error: null,
};

describe("CronSchedulerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<CronSchedulerCard tasks={[enabledTask]} appName="My App" />);
    expect(container.textContent).toContain("Scheduled Tasks");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(
      <CronSchedulerCard tasks={[enabledTask, disabledTask]} appName="App" />,
    );
    expect(container.textContent).toContain("1 active");
  });

  it("shows error badge", () => {
    const { container } = render(<CronSchedulerCard tasks={[failedTask]} appName="App" />);
    expect(container.textContent).toContain("1 errors");
  });

  it("renders task name and schedule", () => {
    const { container } = render(<CronSchedulerCard tasks={[enabledTask]} appName="App" />);
    expect(container.textContent).toContain("Sync Data");
    expect(container.textContent).toContain("every 5 min");
  });

  it("shows run count", () => {
    const { container } = render(<CronSchedulerCard tasks={[enabledTask]} appName="App" />);
    expect(container.textContent).toContain("42 runs");
  });

  it("shows last run time", () => {
    const { container } = render(<CronSchedulerCard tasks={[enabledTask]} appName="App" />);
    expect(container.textContent).toContain("Last:");
  });

  it("shows error message", () => {
    const { container } = render(<CronSchedulerCard tasks={[failedTask]} appName="App" />);
    expect(container.textContent).toContain("SMTP timeout");
  });

  it("shows empty state", () => {
    const { container } = render(<CronSchedulerCard tasks={[]} appName="App" />);
    expect(container.textContent).toContain("No scheduled tasks");
  });
});
