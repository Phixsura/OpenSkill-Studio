import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TaskQueueCard from "../src/components/task-queue-card";

const stats = { pending: 5, running: 2, completed: 100, failed: 3 };
const tasks = [
  {
    task_id: "t1",
    task_type: "email.send",
    priority: 10,
    status: "running" as const,
    attempts: 1,
    max_retries: 3,
  },
  {
    task_id: "t2",
    task_type: "webhook.deliver",
    priority: 5,
    status: "pending" as const,
    attempts: 0,
    max_retries: 3,
  },
];

describe("TaskQueueCard", () => {
  it("renders header and total", () => {
    const { container } = render(<TaskQueueCard stats={stats} recentTasks={tasks} appName="App" />);
    expect(container.textContent).toContain("Task Queue");
    expect(container.textContent).toContain("110 tasks");
  });

  it("shows stats breakdown", () => {
    const { container } = render(<TaskQueueCard stats={stats} recentTasks={tasks} appName="App" />);
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("completed");
  });

  it("shows task types", () => {
    const { container } = render(<TaskQueueCard stats={stats} recentTasks={tasks} appName="App" />);
    expect(container.textContent).toContain("email.send");
    expect(container.textContent).toContain("webhook.deliver");
  });

  it("shows priority and attempts", () => {
    const { container } = render(<TaskQueueCard stats={stats} recentTasks={tasks} appName="App" />);
    expect(container.textContent).toContain("P10");
    expect(container.textContent).toContain("1/3");
  });

  it("shows empty state", () => {
    const { container } = render(
      <TaskQueueCard
        stats={{ pending: 0, running: 0, completed: 0, failed: 0 }}
        recentTasks={[]}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("No tasks");
  });
});
