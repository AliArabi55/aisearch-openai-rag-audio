import { useCallback } from "react";

interface UseAudioSequenceProps {
    onSequenceComplete: () => void;
}

const useAudioSequence = ({ onSequenceComplete }: UseAudioSequenceProps) => {
    
    const playAudioFile = async (src: string, name: string, timeoutMs: number = 10000): Promise<void> => {
        return new Promise((resolve) => {
            console.log(`🎧 بدء تحميل ${name} من ${src}`);
            
            const audio = new Audio(src);
            audio.preload = 'auto';
            audio.volume = 1.0; // تأكد من مستوى الصوت
            
            let resolved = false;
            
            const resolveOnce = (success: boolean = true, message: string = '') => {
                if (!resolved) {
                    resolved = true;
                    if (success) {
                        console.log(`✅ نجح ${name}`);
                        resolve();
                    } else {
                        console.error(`❌ فشل ${name}: ${message}`);
                        resolve(); // نستمر حتى لو فشل
                    }
                }
            };

            // عند انتهاء التشغيل
            audio.onended = () => {
                console.log(`🎉 انتهى تشغيل ${name} بنجاح`);
                resolveOnce(true);
            };

            // عند حدوث خطأ
            audio.onerror = (e) => {
                const errorMsg = `خطأ في تحميل أو تشغيل ${name}`;
                console.error(`❌ ${errorMsg}:`, e);
                resolveOnce(false, errorMsg);
            };

            // عند جاهزية الملف للتشغيل
            audio.oncanplaythrough = () => {
                console.log(`🎵 ${name} جاهز للتشغيل، بدء التشغيل...`);
                
                audio.play()
                    .then(() => {
                        console.log(`🔊 بدء تشغيل ${name} بنجاح`);
                    })
                    .catch((playError) => {
                        const errorMsg = `فشل في تشغيل ${name}: ${playError.message}`;
                        console.error(`❌ ${errorMsg}`);
                        resolveOnce(false, errorMsg);
                    });
            };

            // مهلة زمنية للحماية من التعليق
            setTimeout(() => {
                const timeoutMsg = `انتهت مهلة ${name} (${timeoutMs}ms)`;
                console.warn(`⏰ ${timeoutMsg}`);
                resolveOnce(false, timeoutMsg);
            }, timeoutMs);
        });
    };
    
    const playAudioSequence = useCallback(async () => {
        try {
            console.log("🚀 بدء تسلسل الأصوات الثلاثة...");
            
            // اختبار أولي لفتح سياق الصوت
            try {
                console.log("🔓 فتح سياق الصوت...");
                const testAudio = new Audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmMcAjaL2e7MeSsFJHfH8N2QQAo");
                testAudio.volume = 0.01;
                await testAudio.play();
                console.log("✅ تم فتح سياق الصوت بنجاح");
            } catch (e) {
                console.log("🔇 لم يتم فتح سياق الصوت، المتابعة...");
            }

            // 1. تشغيل Ran.wav (الرنة الأولى)
            console.log("🔔 الخطوة 1: تشغيل Ran.wav...");
            await playAudioFile("/audio/Ran.wav", "Ran.wav", 8000);
            
            // 2. انتظار قصير
            console.log("⏳ الخطوة 2: انتظار 500ms...");
            await new Promise(resolve => setTimeout(resolve, 500));

            // 3. تشغيل between.wav (صوت الانتقال)
            console.log("⚡ الخطوة 3: تشغيل between.wav...");
            await playAudioFile("/audio/between.wav", "between.wav", 5000);
            
            // 4. انتظار قصير
            console.log("⏳ الخطوة 4: انتظار 500ms...");
            await new Promise(resolve => setTimeout(resolve, 500));

            // 5. تشغيل Nancy.wav (صوت الترحيب)
            console.log("🎤 الخطوة 5: تشغيل Nancy.wav...");
            await playAudioFile("/audio/Nancy.wav", "Nancy.wav", 6000);

            // 6. انتظار نهائي قبل تفعيل Real-time
            console.log("⏳ الخطوة 6: انتظار نهائي 1000ms...");
            await new Promise(resolve => setTimeout(resolve, 1000));

            // 7. إشارة انتهاء التسلسل
            console.log("🎉 انتهى تسلسل الأصوات بنجاح، تفعيل Real-time...");
            onSequenceComplete();
            
        } catch (error) {
            console.error("❌ خطأ في تسلسل الأصوات:", error);
            console.error("🔄 المتابعة مع تفعيل Real-time رغم الخطأ...");
            onSequenceComplete(); // استمرار رغم الخطأ
        }
    }, [onSequenceComplete]);

    return {
        playAudioSequence
    };
};

export default useAudioSequence;
