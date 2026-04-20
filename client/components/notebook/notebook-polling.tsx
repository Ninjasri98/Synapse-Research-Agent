"use client";

import { useState, useEffect, useCallback, memo, useRef } from "react";
import {
    Brain,
  Loader2,
  RefreshCw,
  Send,
} from "lucide-react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MarkdownComponents } from "@/components/ui/markdown-components";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { VisualMindmap } from "./visual-mindmap";

// Chat message type
type Message = {
  role: "user" | "assistant";
  content: string;
};

// API response type
type ChatApiResponse = {
  status: "success" | "error";
  response: string;
};

// Memoized message component to prevent re-renders
const ChatMessage = memo(({ message }: { message: Message }) => (
  <div
    className={`flex ${
      message.role === "user" ? "justify-end" : "justify-start"
    }`}
  >
    <div
      className={`max-w-[80%] px-4 py-2 rounded-lg ${
        message.role === "user"
          ? "bg-primary text-primary-foreground"
          : "bg-muted"
      }`}
    >
      {message.role === "assistant" ? (
        <div className="markdown-container prose prose-sm max-w-none dark:prose-invert">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={MarkdownComponents}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      ) : (
        message.content
      )}
    </div>
  </div>
));

ChatMessage.displayName = "ChatMessage";

// Memoized ChatInterface component to prevent unnecessary re-renders
const ChatInterface = memo(
  ({
    messages,
    isLoading,
    onSendMessage,
  }: {
    messages: Message[];
    isLoading: boolean;
    onSendMessage: (message: string) => void;
  }) => {
    // Local state for input to avoid parent component re-renders when typing
    const [localInput, setLocalInput] = useState("");

    // Use callback ref for textarea to ensure focus
    const textareaRef = useCallback((textareaElement: HTMLTextAreaElement) => {
      if (textareaElement) {
        // Focus the textarea on mount
        textareaElement.focus();
      }
    }, []);

    // Ref for the messages container to control scrolling
    const messagesContainerRef = useRef<HTMLDivElement>(null);

    // Scroll to bottom when messages change
    useEffect(() => {
      if (messagesContainerRef.current) {
        messagesContainerRef.current.scrollTop =
          messagesContainerRef.current.scrollHeight;
      }
    }, [messages, isLoading]);

    const handleSubmit = () => {
      if (!localInput.trim()) return;
      onSendMessage(localInput);
      setLocalInput("");
    };

    return (
      <div className="w-full">
        <div
          ref={messagesContainerRef}
          className="flex flex-col space-y-4 mb-4 h-[400px] overflow-y-auto p-4 border rounded-md"
        >
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              Start a conversation with your notebook
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] px-4 py-2 rounded-lg bg-muted flex items-center">
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Thinking...
              </div>
            </div>
          )}
        </div>

        <div className="flex space-x-2">
          <Textarea
            ref={textareaRef}
            rows={1}
            value={localInput}
            onChange={(e) => setLocalInput(e.target.value)}
            placeholder={`Decipher anything about this notebook...`}
            className="resize-none"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
          />
          <Button
            onClick={handleSubmit}
            disabled={isLoading || !localInput.trim()}
            className="px-4"
            data-umami-event="frontend_chat_message_send"
            data-umami-event-notebook-id={window.location.pathname
              .split("/")
              .pop()}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    );
  }
);

ChatInterface.displayName = "ChatInterface";

// FAQ component
const FaqList = memo(
  ({ faqs }: { faqs: { question: string; answer: string }[] }) => {
    if (!faqs || faqs.length === 0) {
      return (
        <div className="flex items-center justify-center h-[400px] text-muted-foreground">
          No FAQs available for this notebook
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {faqs.map((faq, index) => (
          <div key={index} className="space-y-2">
            <h3 className="text-lg font-semibold">{faq.question}</h3>
            <div className="markdown-container prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={MarkdownComponents}
              >
                {faq.answer}
              </ReactMarkdown>
            </div>
          </div>
        ))}
      </div>
    );
  }
);

FaqList.displayName = "FaqList";

// Mindmap Tab Content component
const MindmapTabContent = memo(
  ({
    notebookId,
    initialMindmap,
  }: {
    notebookId: string;
    initialMindmap?: string | null;
  }) => {
    const [mindmap, setMindmap] = useState<string | null>(
      initialMindmap || null
    );
    const [isGenerating, setIsGenerating] = useState(false);

    // Start polling when mindmap is in progress
    useEffect(() => {
      if (mindmap !== "IN_PROGRESS") {
        return;
      }

      const pollInterval = setInterval(async () => {
        try {
          const response = await fetch(`/api/notebooks/${notebookId}`, {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          });

          if (!response.ok) {
            throw new Error("Failed to fetch notebook");
          }

          const notebook = await response.json();
          const newMindmap = notebook.output?.mindmap;

          if (newMindmap && newMindmap !== "IN_PROGRESS") {
            setMindmap(newMindmap);

            if (newMindmap === "ERROR") {
              toast.error("Mindmap generation failed", {
                description: "There was an error generating the mindmap.",
              });
            } else {
              toast.success("Mindmap ready!", {
                description: "Your mindmap has been generated successfully.",
              });
            }
          }
        } catch (error) {
          console.error("Error polling for mindmap:", error);
        }
      }, 3000); // Poll every 3 seconds

      return () => {
        clearInterval(pollInterval);
      };
    }, [mindmap, notebookId]);

    const handleGenerateMindmap = async () => {
      if (isGenerating) return;

      setIsGenerating(true);
      try {
        const response = await fetch(`/api/notebooks/${notebookId}/mindmap`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error("Failed to generate mindmap");
        }

        // Set mindmap to IN_PROGRESS to start polling
        setMindmap("IN_PROGRESS");

        toast.success("Mindmap generation started", {
          description:
            "Your mindmap is being generated. This may take a few minutes.",
        });
      } catch (error) {
        console.error("Error generating mindmap:", error);
        toast.error("Failed to generate mindmap", {
          description: error instanceof Error ? error.message : "Unknown error",
        });
      } finally {
        setIsGenerating(false);
      }
    };

    const handleRetryMindmap = async () => {
      if (isGenerating) return;
      await handleGenerateMindmap();
    };

    if (!mindmap) {
      return (
        <div className="text-center flex flex-col items-center space-y-4 py-8">
          <div className="flex items-center justify-center mb-4">
            <Brain className="h-12 w-12 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold">Generate Mindmap</h3>
          <p className="text-muted-foreground max-w-md mx-auto">
            Generate a visual mindmap of your research to better understand the
            connections and structure.
          </p>
          <Button
            onClick={handleGenerateMindmap}
            disabled={isGenerating}
            className="flex items-center gap-2"
          >
            {isGenerating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Brain className="h-4 w-4" />
            )}
            {isGenerating ? "Generating..." : "Generate Mindmap"}
          </Button>
        </div>
      );
    }

    if (mindmap === "IN_PROGRESS") {
      return (
        <div className="text-center space-y-4 py-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
          <h3 className="text-lg font-semibold">Generating mindmap...</h3>
          <p className="text-muted-foreground max-w-md mx-auto">
            Our AI is analyzing your research and creating a visual mindmap.
            This may take a few minutes.
          </p>
        </div>
      );
    }

    if (mindmap === "ERROR") {
      return (
        <div className="text-center flex flex-col items-center space-y-4 py-8">
          <div className="flex items-center justify-center gap-2 mb-4 text-destructive">
            <Brain className="h-8 w-8" />
          </div>
          <h3 className="text-lg font-semibold text-destructive">
            Generation failed
          </h3>
          <p className="text-muted-foreground max-w-md mx-auto">
            There was an error generating your mindmap. Please try again.
          </p>
          <Button
            onClick={handleRetryMindmap}
            disabled={isGenerating}
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCw
              className={`h-4 w-4 ${isGenerating ? "animate-spin" : ""}`}
            />
            {isGenerating ? "Retrying..." : "Try Again"}
          </Button>
        </div>
      );
    }

    try {
      const mindmapData = JSON.parse(mindmap);
      return (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">{mindmapData.title}</h3>
              <p className="text-muted-foreground text-sm">
                {mindmapData.description}
              </p>
            </div>
          </div>
          <VisualMindmap mindmapData={mindmapData} />
        </div>
      );
    } catch (error) {
      console.error("Error parsing mindmap:", error);
      return (
        <div className="text-center text-muted-foreground py-8">
          Error displaying mindmap. Invalid format.
        </div>
      );
    }
  }
);

MindmapTabContent.displayName = "MindmapTabContent";
