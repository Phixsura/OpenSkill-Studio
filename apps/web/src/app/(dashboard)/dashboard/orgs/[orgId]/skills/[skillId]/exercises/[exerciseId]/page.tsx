"use client";

import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";

interface ExerciseDetail {
  id: string;
  title: string;
  description: string;
  type: string;
  config: Record<string, unknown>;
  max_score: number;
}

interface Attempt {
  id: string;
  score: number | null;
  is_correct: boolean | null;
  feedback: string | null;
  graded_by: string | null;
  created_at: string;
}

export default function ExercisePage() {
  const { orgId, exerciseId } = useParams<{ orgId: string; exerciseId: string }>();
  const queryClient = useQueryClient();

  const { data: exData, isLoading, isError } = useQuery({
    queryKey: ["exercise", exerciseId],
    queryFn: () => apiWithAuth<{ data: ExerciseDetail }>(`/orgs/${orgId}/exercises/${exerciseId}`),
  });

  const { data: attemptData } = useQuery({
    queryKey: ["attempts", exerciseId],
    queryFn: () =>
      apiWithAuth<{ data: Attempt[] }>(`/orgs/${orgId}/exercises/${exerciseId}/attempts`),
  });

  const exercise = exData?.data;
  const attempts = attemptData?.data ?? [];

  const [answer, setAnswer] = useState<Record<string, unknown>>({});
  const [error, setError] = useState<string | null>(null);

  const [lastResult, setLastResult] = useState<Attempt | null>(null);

  const submitMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: Attempt }>(`/orgs/${orgId}/exercises/${exerciseId}/attempts`, {
        method: "POST",
        body: JSON.stringify({ answer }),
      }),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["attempts", exerciseId] });
      setAnswer({});
      setError(null);
      setLastResult(res.data);
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : "Submission failed.");
      setLastResult(null);
    },
  });

  if (isLoading) {
    return <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (isError || !exercise) {
    return <p className="text-[hsl(var(--destructive))]">Failed to load exercise.</p>;
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold">{exercise.title}</h1>
        <p className="mt-2 text-[hsl(var(--muted-foreground))]">{exercise.description}</p>
        <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))] capitalize">
          {exercise.type.replace("_", " ")} · {exercise.max_score} pts
        </p>
      </div>

      {/* Answer area */}
      <div className="rounded-lg border p-6">
        <h2 className="text-sm font-semibold">Your Answer</h2>

        {exercise.type === "multiple_choice" && (
          <MCQInput config={exercise.config} answer={answer} setAnswer={setAnswer} />
        )}
        {exercise.type === "text_answer" && (
          <TextInput answer={answer} setAnswer={setAnswer} />
        )}
        {(exercise.type === "code_submission" || exercise.type === "file_upload") && (
          <TextInput answer={answer} setAnswer={setAnswer} />
        )}

        {error && (
          <p className="mt-3 text-sm text-red-600">{error}</p>
        )}

        <Button
          onClick={() => {
            // Validate answer before submitting
            if (exercise.type === "multiple_choice" && !(answer.selected as string[])?.length) {
              setError("Please select an answer.");
              return;
            }
            if (exercise.type === "text_answer" && !(answer.text as string)?.trim()) {
              setError("Please enter your answer.");
              return;
            }
            setLastResult(null);
            submitMutation.mutate();
          }}
          disabled={submitMutation.isPending}
          className="mt-4"
        >
          {submitMutation.isPending ? "Submitting..." : "Submit"}
        </Button>

        {lastResult && (
          <div className={`mt-4 rounded-md p-4 ${lastResult.is_correct ? "bg-green-50 dark:bg-green-950" : "bg-red-50 dark:bg-red-950"}`}>
            <p className={`font-semibold ${lastResult.is_correct ? "text-green-700 dark:text-green-300" : "text-red-700 dark:text-red-300"}`}>
              {lastResult.is_correct ? "✅ Correct!" : "❌ Incorrect"} — {lastResult.score}/{exercise.max_score} pts
            </p>
            {lastResult.feedback && (
              <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">{lastResult.feedback}</p>
            )}
          </div>
        )}
      </div>

      {/* Attempt history */}
      {attempts.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold">Previous Attempts</h2>
          <div className="mt-3 space-y-3">
            {attempts.map((a) => (
              <div key={a.id} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[hsl(var(--muted-foreground))]">
                    {new Date(a.created_at).toLocaleString()}
                  </span>
                  {a.score !== null && (
                    <span
                      className={`font-mono text-sm font-bold ${a.is_correct ? "text-green-600" : "text-red-600"}`}
                    >
                      {a.score}/{exercise.max_score}
                    </span>
                  )}
                  {a.score === null && (
                    <span className="text-xs text-yellow-600">Pending review</span>
                  )}
                </div>
                {a.feedback && (
                  <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">{a.feedback}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── MCQ ──

function MCQInput({
  config,
  answer,
  setAnswer,
}: {
  config: Record<string, unknown>;
  answer: Record<string, unknown>;
  setAnswer: (a: Record<string, unknown>) => void;
}) {
  const options = (config.options as { id: string; text: string }[]) ?? [];
  const multiple = config.multiple as boolean ?? false;
  const selected = ((answer.selected as string[]) ?? []);

  const toggle = (id: string) => {
    if (multiple) {
      const next = selected.includes(id)
        ? selected.filter((s) => s !== id)
        : [...selected, id];
      setAnswer({ selected: next });
    } else {
      setAnswer({ selected: [id] });
    }
  };

  return (
    <div className="mt-4 space-y-2">
      {options.map((opt) => (
        <label
          key={opt.id}
          className={`flex cursor-pointer items-center gap-3 rounded-md border p-3 text-sm transition-colors ${
            selected.includes(opt.id) ? "border-[hsl(var(--primary))] bg-[hsl(var(--secondary))]" : ""
          }`}
        >
          <input
            type={multiple ? "checkbox" : "radio"}
            name="mcq"
            checked={selected.includes(opt.id)}
            onChange={() => toggle(opt.id)}
            className="accent-[hsl(var(--primary))]"
          />
          {opt.text}
        </label>
      ))}
    </div>
  );
}

// ── Text ──

function TextInput({
  answer,
  setAnswer,
}: {
  answer: Record<string, unknown>;
  setAnswer: (a: Record<string, unknown>) => void;
}) {
  return (
    <textarea
      value={(answer.text as string) ?? ""}
      onChange={(e) => setAnswer({ text: e.target.value })}
      rows={6}
      className="mt-4 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
      placeholder="Enter your answer..."
    />
  );
}
