import "./status-message.css";
import { useTranslation } from "react-i18next";

type Properties = {
    isRecording: boolean;
    isPlayingSequence?: boolean;
    remainingTime?: number;
    showGoodbyeMessage?: boolean;
};

export default function StatusMessage({ 
    isRecording, 
    isPlayingSequence = false, 
    remainingTime = 180,
    showGoodbyeMessage = false 
}: Properties) {
    const { t } = useTranslation();

    // 🆕 Format time for display
    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // 🆕 Show goodbye message
    if (showGoodbyeMessage) {
        return (
            <div className="mb-4 mt-6 text-center">
                <p className="text-lg text-green-600 font-semibold">👋 شكراً لك! جاري إنهاء المحادثة...</p>
            </div>
        );
    }

    if (isPlayingSequence) {
        return <p className="text mb-4 mt-6 text-yellow-600">جاري تحضير الاتصال... استمع للتعليمات</p>;
    }

    if (!isRecording) {
        return <p className="text mb-4 mt-6">{t("status.notRecordingMessage")}</p>;
    }

    return (
        <div className="mb-4 mt-6 text-center">
            <div className="flex items-center justify-center mb-2">
                <div className="relative h-6 w-6 overflow-hidden">
                    <div className="absolute inset-0 flex items-end justify-around">
                        {[...Array(4)].map((_, i) => (
                            <div
                                key={i}
                                className="w-1 rounded-full bg-purple-600 opacity-80"
                                style={{
                                    animation: `barHeight${(i % 3) + 1} 1s ease-in-out infinite`,
                                    animationDelay: `${i * 0.1}s`
                                }}
                            />
                        ))}
                    </div>
                </div>
                <p className="text ml-2">{t("status.conversationInProgress")}</p>
            </div>
            {/* 🆕 Countdown timer */}
            <div className="text-sm text-gray-600">
                <span className="font-mono bg-gray-100 px-2 py-1 rounded">
                    ⏱️ {formatTime(remainingTime)}
                </span>
                <p className="text-xs mt-1">سيتم إنهاء المحادثة تلقائياً عند انتهاء الوقت</p>
            </div>
        </div>
    );
}
