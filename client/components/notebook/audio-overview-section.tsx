"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { AudioPlayer } from "@/components/ui/audio-player";
import { Loader2, Volume2, AlertCircle, RefreshCw } from "lucide-react";
import { toast } from "sonner";

interface AudioOverviewSectionProps {
  notebookId: string;
  initialAudioOverviewUrl?: string | null;
}

export function AudioOverviewSection({
  notebookId,
  initialAudioOverviewUrl,
}: AudioOverviewSectionProps) {
  const [audioOverviewUrl, setAudioOverviewUrl] = useState<string | null>(
    initialAudioOverviewUrl || null
  );
  const [isGenerating, setIsGenerating] = useState(false);

  // Start polling when audio overview is in progress
  useEffect(() => {
    if (audioOverviewUrl !== "IN_PROGRESS") {
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
        const newAudioUrl = notebook.output?.audioOverviewUrl;

        if (newAudioUrl && newAudioUrl !== "IN_PROGRESS") {
          setAudioOverviewUrl(newAudioUrl);

          if (newAudioUrl === "ERROR") {
            toast.error("Audio overview generation failed", {
              description: "There was an error generating the audio overview.",
            });
          } else {
            toast.success("Audio overview ready!", {
              description:
                "Your audio overview has been generated successfully.",
            });
          }
        }
      } catch (error) {
        console.error("Error polling for audio overview:", error);
      }
    }, 3000); // Poll every 3 seconds

    return () => {
      clearInterval(pollInterval);
    };
  }, [audioOverviewUrl, notebookId]);

  const handleGenerateAudio = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch(
        `/api/notebooks/${notebookId}/audio-overview`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to generate audio overview");
      }

      setAudioOverviewUrl("IN_PROGRESS");
      toast.success("Audio overview generation started", {
        description:
          "We're generating your audio overview. This may take a few minutes.",
      });
    } catch (error) {
      console.error("Error generating audio overview:", error);
      toast.error("Failed to generate audio overview", {
        description: error instanceof Error ? error.message : "Unknown error",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRetry = async () => {
    setAudioOverviewUrl(null);
    await handleGenerateAudio();
  };

  // Don't render anything if audio overview URL is null (not generated yet)
  if (!audioOverviewUrl) {
    return (
      <Card className="w-full">
        <CardContent>
          <div className="text-center space-y-2">
            <p className="text-muted-foreground">
              Generate an AI-powered audio overview of your research notebook.
            </p>
            <span className="text-xs text-muted-foreground">
              The voice and content are AI-generated and may contain
              inaccuracies or audio glitches.
            </span>
            <div className="flex justify-center mt-4">
              <Button
                onClick={handleGenerateAudio}
                disabled={isGenerating}
                className="flex items-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Volume2 className="h-4 w-4" />
                    Generate Audio Overview
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show loading state while generating
  if (audioOverviewUrl === "IN_PROGRESS") {
    return (
      <Card className="w-full">
        <CardContent>
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
              <span className="text-lg font-medium">
                Generating Audio Overview...
              </span>
            </div>
            <p className="text-muted-foreground">
              Our AI is creating an audio summary of your research. This may
              take a few minutes.
            </p>
            <span className="text-xs text-muted-foreground">
              The voice and content are AI-generated and may contain
              inaccuracies or audio glitches.
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show error state
  if (audioOverviewUrl === "ERROR") {
    return (
      <Card className="w-full">
        <CardContent>
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2 text-destructive">
              <AlertCircle className="h-6 w-6" />
              <span className="text-lg font-medium">Generation Failed</span>
            </div>
            <p className="text-muted-foreground">
              There was an error generating the audio overview. Please try
              again.
            </p>
            <Button
              onClick={handleRetry}
              disabled={isGenerating}
              variant="outline"
              className="flex items-center gap-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Retrying...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  Try Again
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show audio player when URL is available
  return (
    <div className="space-y-4">
      <Card className="w-full">
        <CardHeader>
          <p className="text-sm text-muted-foreground mt-2">
            Listen to an AI-generated deep dive discussion that summarizes the
            key topics from your sources. <br />
            <span className="text-xs text-muted-foreground">
              The voice and content are AI-generated and may contain
              inaccuracies or audio glitches.
            </span>
          </p>
        </CardHeader>
        <CardContent>
          <AudioPlayer src={audioOverviewUrl} />
        </CardContent>
      </Card>
    </div>
  );
}
