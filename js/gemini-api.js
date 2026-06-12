/* ============================================
   GROQ API - AI Connection (remplace Gemini)
   ============================================ */

const GeminiAPI = {
  API_KEY: 'VOTRE_CLE_GROQ_ICI', // à remplacer ou à configurer via le backend

  API_URL: 'https://api.groq.com/openai/v1/chat/completions',

  MODEL: 'llama-3.3-70b-versatile',

  SYSTEM_PROMPT: `أنت "أستاذ خوارزمي"، مساعد ذكي متخصص في علوم الطبيعة والحياة لطلاب البكالوريا في الجزائر.

قواعد مهمة:
1. أجب باللغة العربية بشكل افتراضي، إلا إذا طُلب منك الإجابة بالفرنسية
2. ركّز على المنهاج الجزائري للسنة الثالثة ثانوي - شعبة العلوم التجريبية
3. المواضيع الرئيسية: تركيب البروتين، المناعة، الاتصال العصبي، علم الوراثة، التطور
4. قدّم إجابات واضحة ومنظمة مع أمثلة
5. استخدم الرموز التعبيرية باعتدال لجعل الشرح أكثر جاذبية
6. عند الإمكان، اربط المفاهيم بأسئلة بكالوريا سابقة
7. شجّع الطالب وكن إيجابياً
8. إذا لم تعرف الإجابة، قل ذلك بصراحة ولا تخترع معلومات

كن دائماً مهنياً، مفيداً ومحفزاً!`,

  async sendMessage(userMessage, conversationHistory = []) {
    try {
      const messages = [
        { role: 'system', content: this.SYSTEM_PROMPT },
        { role: 'assistant', content: 'فهمت! أنا أستاذ خوارزمي، جاهز لمساعدة طلاب البكالوريا الجزائريين. كيف يمكنني مساعدتك اليوم؟' }
      ];

      conversationHistory.forEach(msg => {
        messages.push({
          role: msg.role === 'model' ? 'assistant' : 'user',
          content: msg.parts[0].text
        });
      });

      messages.push({ role: 'user', content: userMessage });

      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.API_KEY}`
        },
        body: JSON.stringify({
          model: this.MODEL,
          messages: messages,
          temperature: 0.7,
          max_tokens: 1024,
          top_p: 0.95
        })
      });

      if (!response.ok) {
        const errBody = await response.text().catch(() => '');
        throw new Error(`API ${response.status}: ${errBody.slice(0, 200)}`);
      }

      const data = await response.json();

      if (data.choices && data.choices[0]?.message?.content) {
        return {
          success: true,
          message: data.choices[0].message.content
        };
      } else {
        throw new Error('Réponse invalide de Groq');
      }

    } catch (error) {
      console.error('Groq API Error:', error);
      return this.getFallbackResponse(userMessage);
    }
  },

  getFallbackResponse(userMessage) {
    const lowerMsg = userMessage.toLowerCase();

    let response = '';

    if (lowerMsg.includes('استنساخ') || lowerMsg.includes('transcription')) {
      response = `📚 **عملية الاستنساخ (Transcription)**\n\nهي عملية نسخ المعلومة الوراثية من ADN إلى ARNm داخل النواة.\n\n**المراحل:**\n1️⃣ الانطلاق: ارتباط ARN بوليمراز\n2️⃣ الاستطالة: قراءة وبناء ARN\n3️⃣ النهاية: انفصال الإنزيم\n\n💡 نصيحة: راجع جيداً دور إنزيم ARN polymérase لأنه سؤال متكرر في البكالوريا!`;
    } else if (lowerMsg.includes('ترجمة') || lowerMsg.includes('translation')) {
      response = `🔄 **عملية الترجمة (Translation)**\n\nتحويل المعلومة من ARNm إلى بروتين في الهيولى على الريبوزومات.\n\n**العناصر الأساسية:**\n• ARNm (الرسالة)\n• الريبوزومات (المقر)\n• ARNt (الناقل)\n• الأحماض الأمينية\n\nهل تريد أن أشرح لك مراحل الترجمة بالتفصيل؟ 🎯`;
    } else if (lowerMsg.includes('شفرة') || lowerMsg.includes('code')) {
      response = `🔤 **الشفرة الوراثية**\n\nنظام مراسلة بين 4 قواعد و20 حمض أميني.\n\n**أرقام مهمة:**\n• 64 رامزة إجمالاً\n• 61 رامزة تشفير\n• 3 رامزات توقف (UAA, UAG, UGA)\n• 1 رامزة انطلاق (AUG)\n\n💎 خصائص الشفرة: عالمية، تنكسية، غير متراكبة، محددة.`;
    } else if (lowerMsg.includes('سلام') || lowerMsg.includes('مرحبا') || lowerMsg.includes('hello')) {
      response = `أهلاً وسهلاً! 👋\n\nأنا **أستاذ خوارزمي**، مساعدك الذكي للنجاح في البكالوريا.\n\nيمكنني مساعدتك في:\n📚 شرح الدروس\n🧪 توليد اختبارات\n📝 تصحيح إجاباتك\n💡 نصائح للمراجعة\n\nبماذا تريد أن نبدأ؟ 🚀`;
    } else if (lowerMsg.includes('اختبار') || lowerMsg.includes('سؤال') || lowerMsg.includes('quiz')) {
      response = `🧪 **سؤال للاختبار:**\n\nما هي مراحل عملية الاستنساخ؟ وما هو دور إنزيم ARN بوليمراز في كل مرحلة؟\n\n💭 خذ وقتك للتفكير، ثم أرسل لي إجابتك وسأقوم بتصحيحها!`;
    } else {
      response = `شكراً على سؤالك! 🌟\n\nيمكنني مساعدتك في:\n• تركيب البروتين 🧬\n• الشفرة الوراثية 🔤\n• الترجمة 🔄\n• المناعة 🛡️\n• وأي موضوع من برنامج البكالوريا!`;
    }

    return {
      success: true,
      message: response,
      isDemo: true
    };
  }
};
