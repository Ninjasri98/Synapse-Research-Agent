"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useState, useEffect } from "react";

const notebookSchema = z.object({
  topic: z
    .string()
    .transform((val) => (val === "" ? undefined : val))
    .optional(),
});

export function CreateNotebookDialog() {
  const router = useRouter();
  const [sources, setSources] = useState<
    {
      type: "URL" | "TEXT" | "FILE";
      value: string;
      filename?: string;
      filePath?: string;
    }[]
  >([]);
  const [currentSource, setCurrentSource] = useState<"URL" | "TEXT" | "FILE">(
    "URL"
  );
  const [sourceValue, setSourceValue] = useState("");
  const [sourceError, setSourceError] = useState("");
  const [formError, setFormError] = useState("");
  const [activeTab, setActiveTab] = useState<"TOPIC" | "SOURCES">("TOPIC");

  const form = useForm<z.infer<typeof notebookSchema>>({
    resolver: zodResolver(notebookSchema),
    defaultValues: {
      topic: "",
    },
  });

  const addSource = () => {
    if (currentSource === "FILE") {
      // File sources are added via the FileUpload component
      return;
    }

    if (!sourceValue.trim()) {
      setSourceError("Source cannot be empty");
      return;
    }

    if (currentSource === "URL" && !isValidUrl(sourceValue)) {
      setSourceError("Please enter a valid URL");
      return;
    }

    setSources([...sources, { type: currentSource, value: sourceValue }]);
    setSourceValue("");
    setSourceError("");
    setFormError("");
  };

  const removeSource = (index: number) => {
    const newSources = [...sources];
    newSources.splice(index, 1);
    setSources(newSources);
  };

  const isValidUrl = (url: string) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleFileUpload = (result: {
    filePath: string;
    filename: string;
    fileSize: number;
    fileType: string;
    publicUrl: string;
  }) => {
    setSources([
      ...sources,
      {
        type: "FILE",
        value: result.publicUrl,
        filename: result.filename,
        filePath: result.filePath,
      },
    ]);
    setSourceError("");
    setFormError("");
  };

  const handleFileUploadError = (error: string) => {
    setSourceError(error);
  };

  async function onSubmit(values: z.infer<typeof notebookSchema>) {
    try {
      // Validation: only require the active input
      if (activeTab === "TOPIC") {
        if (!values.topic || values.topic.trim() === "") {
          setFormError("Please provide a topic");
          return;
        }
        if (values.topic.trim().length < 3) {
          form.setError("topic", {
            type: "manual",
            message: "Topic must be at least 3 characters",
          });
          return;
        }
        if (values.topic.trim().length > 200) {
          form.setError("topic", {
            type: "manual",
            message: "Topic must be less than 200 characters",
          });
          return;
        }
      } else if (activeTab === "SOURCES") {
        if (sources.length === 0) {
          setFormError("Please add at least one source");
          return;
        }
      }

      const sourcesToSave = sources.map((source) => {
        if (source.type === "URL") {
          return {
            sourceType: "URL",
            sourceUrl: source.value,
          };
        } else if (source.type === "FILE") {
          return {
            sourceType: "UPLOAD",
            sourceUrl: source.value,
            filePath: source.filePath,
            filename: source.filename,
          };
        } else {
          return {
            sourceType: "MANUAL",
            content: source.value,
          };
        }
      });

      const response = await fetch("/api/notebooks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic:
            activeTab === "TOPIC" && values.topic && values.topic.trim()
              ? values.topic.trim()
              : null,
          sources: activeTab === "SOURCES" ? sourcesToSave : [],
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create notebook");
      }

      form.reset();
      setSources([]);
      setSourceValue("");
      toast.success("Notebook created successfully");
      router.push(`/notebook/${await response.json().then((data) => data.id)}`);
      router.refresh();
    } catch (error) {
      console.error("Error creating notebook:", error);
      toast.error("Failed to create notebook");
    }
  }

  useEffect(() => {
    // Clear errors when form values change
    const subscription = form.watch(() => {
      setFormError("");
    });
    return () => subscription.unsubscribe();
  }, [form]);
  return(
    <div></div>
  )
}