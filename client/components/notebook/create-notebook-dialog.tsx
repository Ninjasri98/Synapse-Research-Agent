"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { FileUpload } from "@/components/ui/file-upload";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { useState, useEffect } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

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

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          data-umami-event="frontend_create_notebook_dialog_open"
          data-umami-event-section="dashboard"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Notebook
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader className="space-y-3 pb-4">
          <DialogTitle className="text-xl font-semibold">
            Create New Notebook
          </DialogTitle>
          <DialogDescription className="text-base text-muted-foreground">
            Start by choosing a topic or add your own sources to build a
            comprehensive research notebook.
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto">
          <Tabs
            value={activeTab}
            onValueChange={(v) => setActiveTab(v as "TOPIC" | "SOURCES")}
            className="w-full h-full"
          >
            <TabsList className="mb-6 w-full grid grid-cols-2 bg-muted/50">
              <TabsTrigger
                value="TOPIC"
                className="flex-1 data-[state=active]:bg-background"
              >
                Topic
              </TabsTrigger>
              <TabsTrigger
                value="SOURCES"
                className="flex-1 data-[state=active]:bg-background"
              >
                Sources
              </TabsTrigger>
            </TabsList>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-6"
              >
                <TabsContent value="TOPIC" className="mt-0">
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="topic"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base font-medium">
                            Research Topic
                          </FormLabel>
                          <FormControl>
                            <Input
                              placeholder="e.g., Climate change impacts on marine ecosystems"
                              {...field}
                              className="h-12 text-base"
                              onChange={(e) => {
                                field.onChange(e);
                                setFormError("");
                              }}
                            />
                          </FormControl>
                          <FormDescription className="text-sm">
                            Describe what you want to research and learn about
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    {formError && (
                      <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-lg">
                        {formError}
                      </div>
                    )}
                  </div>
                </TabsContent>
                <TabsContent value="SOURCES">
                  <div className="space-y-6">
                    <div className="space-y-2">
                      <FormLabel className="text-base font-medium">
                        Add Sources (Up to 20)
                      </FormLabel>
                      <p className="text-sm text-muted-foreground">
                        Choose from URLs, text content, or upload documents to
                        include in your notebook.
                      </p>
                    </div>

                    <div className="space-y-4">
                      <Select
                        value={currentSource}
                        onValueChange={(value: string) => {
                          setCurrentSource(value as "URL" | "TEXT" | "FILE");
                          setSourceValue("");
                          setSourceError("");
                        }}
                      >
                        <SelectTrigger className="w-[140px]">
                          <SelectValue placeholder="Source Type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="URL">URL</SelectItem>
                          <SelectItem value="TEXT">Text</SelectItem>
                          <SelectItem value="FILE">File</SelectItem>
                        </SelectContent>
                      </Select>

                      {currentSource === "FILE" ? (
                        <FileUpload
                          onFileUpload={handleFileUpload}
                          onError={handleFileUploadError}
                          disabled={sources.length >= 20}
                          className="w-full"
                        />
                      ) : (
                        <div className="space-y-3">
                          {currentSource === "URL" ? (
                            <div className="flex gap-2">
                              <Input
                                placeholder="https://example.com/article"
                                value={sourceValue}
                                onChange={(e) => setSourceValue(e.target.value)}
                                disabled={sources.length >= 20}
                                className="flex-1"
                              />
                              <Button
                                type="button"
                                onClick={addSource}
                                disabled={
                                  sources.length >= 20 || !sourceValue.trim()
                                }
                                size="default"
                                data-umami-event="frontend_source_add_click"
                                data-umami-event-source-type="URL"
                              >
                                Add
                              </Button>
                            </div>
                          ) : (
                            <div className="space-y-3">
                              <Textarea
                                placeholder="Paste your text content here..."
                                value={sourceValue}
                                onChange={(e) => setSourceValue(e.target.value)}
                                disabled={sources.length >= 20}
                                className="min-h-[120px] resize-y"
                              />
                              <div className="flex justify-end">
                                <Button
                                  type="button"
                                  onClick={addSource}
                                  disabled={
                                    sources.length >= 20 || !sourceValue.trim()
                                  }
                                  size="default"
                                  data-umami-event="frontend_source_add_click"
                                  data-umami-event-source-type="TEXT"
                                >
                                  Add
                                </Button>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    {sourceError && (
                      <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-lg">
                        {sourceError}
                      </div>
                    )}

                    {formError && (
                      <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-lg">
                        {formError}
                      </div>
                    )}

                    {sources.length > 0 && (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-medium">
                            Added Sources ({sources.length}/20)
                          </h3>
                          <p className="text-xs text-muted-foreground">
                            {20 - sources.length} remaining
                          </p>
                        </div>
                        <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2 border rounded-lg bg-muted/30 p-3">
                          {sources.map((source, index) => (
                            <div
                              key={index}
                              className="flex items-start justify-between p-3 border rounded-lg bg-background shadow-sm hover:shadow-md transition-shadow"
                            >
                              <div className="flex items-start flex-1 overflow-hidden mr-3">
                                <span
                                  className={cn(
                                    "text-xs px-2.5 py-1 rounded-full mr-3 shrink-0 font-medium",
                                    source.type === "URL" &&
                                      "bg-blue-100 text-blue-700",
                                    source.type === "TEXT" &&
                                      "bg-green-100 text-green-700",
                                    source.type === "FILE" &&
                                      "bg-purple-100 text-purple-700"
                                  )}
                                >
                                  {source.type}
                                </span>
                                <div className="overflow-hidden flex-1">
                                  <p className="text-sm font-medium truncate">
                                    {source.type === "FILE"
                                      ? source.filename || "Uploaded file"
                                      : source.value.length > 60
                                      ? `${source.value.substring(0, 60)}...`
                                      : source.value}
                                  </p>
                                  {source.type === "TEXT" &&
                                    source.value.length > 60 && (
                                      <p className="text-xs text-muted-foreground mt-1">
                                        {source.value.length} characters
                                      </p>
                                    )}
                                </div>
                              </div>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => removeSource(index)}
                                className="shrink-0 h-8 w-8 p-0 hover:bg-destructive/10 hover:text-destructive"
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </TabsContent>
                <DialogFooter className="flex flex-col sm:flex-row gap-3 pt-6 mt-6 border-t">
                  <DialogClose asChild>
                    <Button
                      variant="outline"
                      type="button"
                      className="w-full sm:w-auto order-2 sm:order-1"
                    >
                      Cancel
                    </Button>
                  </DialogClose>
                  <Button
                    type="submit"
                    className="w-full sm:w-auto order-1 sm:order-2 bg-linear-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary/80"
                    data-umami-event="frontend_notebook_create_submit"
                    data-umami-event-tab={activeTab}
                    data-umami-event-sources-count={sources.length}
                  >
                    Synapse
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
}
