import { useState, useEffect, useRef } from "react";
import { Mic, MicOff } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { GroundingFiles } from "@/components/ui/grounding-files";
import GroundingFileView from "@/components/ui/grounding-file-view";
import StatusMessage from "@/components/ui/status-message";
import OrderDisplay from "@/components/ui/order-display";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";
import useAudioSequence from "@/hooks/useAudioSequence";

import { GroundingFile, ToolResult, OrderItem } from "./types";

import logo from "./assets/Circles png.png";

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [isPlayingSequence, setIsPlayingSequence] = useState(false);
    const [groundingFiles, setGroundingFiles] = useState<GroundingFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<GroundingFile | null>(null);

    // Order management state
    const [orderItems, setOrderItems] = useState<OrderItem[]>([]);
    const [totalPrice, setTotalPrice] = useState(0);
    const [showOrder, setShowOrder] = useState(true); // Always show order table

    // 🆕 Timer state for countdown
    const [remainingTime, setRemainingTime] = useState(180); // 3 minutes = 180 seconds
    const [showGoodbyeMessage, setShowGoodbyeMessage] = useState(false);

    // Auto-disconnect timer (3 minutes = 180000 ms)
    const inactivityTimerRef = useRef<NodeJS.Timeout | null>(null);
    const countdownTimerRef = useRef<NodeJS.Timeout | null>(null);
    const INACTIVITY_TIMEOUT = 3 * 60 * 1000; // 3 minutes

    // Auto-disconnect function
    const disconnectCall = async () => {
        console.log("Disconnecting call...");
        
        if (isRecording) {
            console.log("Stopping audio recording...");
            await stopAudioRecording();
            stopAudioPlayer();
            inputAudioBufferClear();
        }
        
        // Reset all states
        setIsRecording(false);
        setIsPlayingSequence(false);
        setShowGoodbyeMessage(false);
        setRemainingTime(180); // Reset timer
        
        // Clear timers
        if (inactivityTimerRef.current) {
            clearTimeout(inactivityTimerRef.current);
            inactivityTimerRef.current = null;
        }
        
        if (countdownTimerRef.current) {
            clearInterval(countdownTimerRef.current);
            countdownTimerRef.current = null;
        }
        
        console.log("✅ Call disconnected and all states reset");
    };

    // 🆕 Start countdown timer
    const startCountdownTimer = () => {
        setRemainingTime(180); // Reset to 3 minutes
        
        countdownTimerRef.current = setInterval(() => {
            setRemainingTime(prev => {
                if (prev <= 1) {
                    // Time's up - disconnect
                    disconnectCall();
                    return 180;
                }
                return prev - 1;
            });
        }, 1000);
    };

    // 🆕 Stop countdown timer
    const stopCountdownTimer = () => {
        if (countdownTimerRef.current) {
            clearInterval(countdownTimerRef.current);
            countdownTimerRef.current = null;
        }
        setRemainingTime(180); // Reset timer
    };

    // Reset activity timer
    const resetActivityTimer = () => {
        if (inactivityTimerRef.current) {
            clearTimeout(inactivityTimerRef.current);
        }
        if (isRecording) {
            inactivityTimerRef.current = setTimeout(disconnectCall, INACTIVITY_TIMEOUT);
        }
    };

    // Monitor inactivity and countdown
    useEffect(() => {
        if (isRecording) {
            resetActivityTimer();
            startCountdownTimer(); // Start countdown when recording starts
        } else {
            if (inactivityTimerRef.current) {
                clearTimeout(inactivityTimerRef.current);
                inactivityTimerRef.current = null;
            }
            stopCountdownTimer(); // Stop countdown when recording stops
        }

        return () => {
            if (inactivityTimerRef.current) {
                clearTimeout(inactivityTimerRef.current);
            }
            if (countdownTimerRef.current) {
                clearInterval(countdownTimerRef.current);
            }
        };
    }, [isRecording]);

    const { startSession, addUserAudio, inputAudioBufferClear } = useRealTime({
        onWebSocketOpen: () => {
            console.log("WebSocket connection opened");
            resetActivityTimer();
        },
        onWebSocketClose: () => console.log("WebSocket connection closed"),
        onWebSocketError: event => console.error("WebSocket error:", event),
        onReceivedError: message => console.error("error", message),
        onReceivedResponseAudioDelta: message => {
            isRecording && playAudio(message.delta);
            resetActivityTimer(); // Reset timer on AI response
        },
        onReceivedInputAudioBufferSpeechStarted: () => {
            console.log("Speech started detected");
            stopAudioPlayer();
            resetActivityTimer(); // Reset timer on user speech
        },
        onReceivedExtensionMiddleTierToolResponse: message => {
            resetActivityTimer(); // Reset timer on tool response
            console.log("🔧 Tool Response Received:", message.tool_result);
            try {
                const result: ToolResult = JSON.parse(message.tool_result);
                console.log("📊 Parsed Tool Result:", result);

                // Handle order management messages
                if (result.action) {
                    console.log("🎯 Action Detected:", result.action);
                    switch (result.action) {
                        case "order_updated":
                        case "show_order_summary":
                            if (result.order_summary) {
                                console.log("📝 Order Summary:", result.order_summary);
                                setOrderItems(result.order_summary.items);
                                setTotalPrice(result.order_summary.total_price);
                                setShowOrder(true);
                                console.log("✅ Order state updated");
                            }
                            break;
                        case "order_confirmed":
                            console.log("✅ Order confirmed, hiding after 5 seconds");
                            // Show confirmation and hide order after a delay
                            setTimeout(() => {
                                setShowOrder(false);
                                setOrderItems([]);
                                setTotalPrice(0);
                            }, 5000);
                            break;
                        case "order_cleared":
                            console.log("🗑️ Order cleared");
                            setShowOrder(false);
                            setOrderItems([]);
                            setTotalPrice(0);
                            break;
                        case "end_conversation":
                            console.log("👋 User said goodbye, ending conversation");
                            setShowGoodbyeMessage(true);
                            
                            // إنهاء المكالمة بعد عرض الرسالة لثانيتين
                            setTimeout(async () => {
                                await disconnectCall();
                            }, 2000);
                            break;
                    }
                }

                // Handle grounding files (existing functionality)
                if (result.sources) {
                    const files: GroundingFile[] = result.sources.map(x => {
                        return { id: x.chunk_id, name: x.title, content: x.chunk };
                    });
                    setGroundingFiles(prev => [...prev, ...files]);
                }
            } catch (error) {
                console.error("Error parsing tool result:", error);
                // Fallback for old format
                const result: ToolResult = JSON.parse(message.tool_result);
                if (result.sources) {
                    const files: GroundingFile[] = result.sources.map(x => {
                        return { id: x.chunk_id, name: x.title, content: x.chunk };
                    });
                    setGroundingFiles(prev => [...prev, ...files]);
                }
            }
        }
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({ onAudioRecorded: addUserAudio });

    // Hook للتسلسل الصوتي
    const { playAudioSequence } = useAudioSequence({
        onSequenceComplete: async () => {
            // بعد انتهاء تسلسل الأصوات بالكامل، بدء الريل تايم
            console.log("Audio sequence completed, starting realtime...");
            setIsPlayingSequence(false);
            setIsRecording(true);

            // بدء جلسة الريل تايم
            startSession();

            // بدء تسجيل الصوت
            await startAudioRecording();
            resetAudioPlayer();
        }
    });

    const onToggleListening = async () => {
        console.log("onToggleListening called. isRecording:", isRecording, "isPlayingSequence:", isPlayingSequence);

        if (!isRecording && !isPlayingSequence) {
            // بدء تسلسل الأصوات
            console.log("Starting audio sequence...");
            setIsPlayingSequence(true);
            playAudioSequence();
        } else if (isRecording) {
            console.log("Stopping recording...");
            await stopAudioRecording();
            stopAudioPlayer();
            inputAudioBufferClear();
            setIsRecording(false);
        }
    };

    const { t } = useTranslation();

    // Debug: Log order state changes
    useEffect(() => {
        console.log("🛒 Order State Changed:");
        console.log("  - showOrder:", showOrder);
        console.log("  - orderItems:", orderItems);
        console.log("  - totalPrice:", totalPrice);
    }, [showOrder, orderItems, totalPrice]);

    return (
        <div className="flex min-h-screen flex-col bg-gray-100 text-gray-900">
            <div className="p-4 sm:absolute sm:left-4 sm:top-4">
                <img src={logo} alt="Circles Restaurant logo" className="h-16 w-16" />
            </div>
            <main className="flex flex-grow flex-col items-center justify-center">
                <h1 className="mb-8 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-4xl font-bold text-transparent md:text-7xl">
                    {t("app.title")}
                </h1>
                
                {/* Order Display - Show below title */}
                <OrderDisplay orderItems={orderItems} totalPrice={totalPrice} isVisible={showOrder} />
                
                <div className="mb-4 flex flex-col items-center justify-center">
                    <Button
                        onClick={onToggleListening}
                        className={`h-12 w-60 ${
                            isRecording
                                ? "bg-red-600 hover:bg-red-700"
                                : isPlayingSequence
                                  ? "bg-yellow-500 hover:bg-yellow-600"
                                  : "bg-purple-500 hover:bg-purple-600"
                        }`}
                        disabled={isPlayingSequence}
                        aria-label={isRecording ? t("app.stopRecording") : isPlayingSequence ? "جاري التحضير..." : t("app.startRecording")}
                    >
                        {isRecording ? (
                            <>
                                <MicOff className="mr-2 h-4 w-4" />
                                {t("app.stopConversation")}
                            </>
                        ) : isPlayingSequence ? (
                            <>
                                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                                جاري التحضير...
                            </>
                        ) : (
                            <>
                                <Mic className="mr-2 h-6 w-6" />
                                اتصال
                            </>
                        )}
                    </Button>
                    <StatusMessage 
                        isRecording={isRecording} 
                        isPlayingSequence={isPlayingSequence} 
                        remainingTime={remainingTime}
                        showGoodbyeMessage={showGoodbyeMessage}
                    />
                </div>
                <GroundingFiles files={groundingFiles} onSelected={setSelectedFile} />
            </main>

            <footer className="py-4 text-center">
                <p>{t("app.footer")}</p>
            </footer>

            <GroundingFileView groundingFile={selectedFile} onClosed={() => setSelectedFile(null)} />
        </div>
    );
}

export default App;
