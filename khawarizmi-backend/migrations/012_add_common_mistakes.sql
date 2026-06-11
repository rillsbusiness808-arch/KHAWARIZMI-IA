-- Migration 012 : Common Mistakes (Erreurs fréquentes)
-- Feedback instantané sans LLM → 80% d'économie de tokens

CREATE TABLE IF NOT EXISTS common_mistakes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapitre_id     VARCHAR(32) NOT NULL,
    error_type      VARCHAR(20) NOT NULL,
    error_pattern   TEXT NOT NULL,
    frequency       FLOAT DEFAULT 0.5,
    feedback_ar     TEXT NOT NULL,
    feedback_fr     TEXT,
    feynman_prompt  TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mistakes_chapitre ON common_mistakes (chapitre_id);
CREATE INDEX IF NOT EXISTS idx_mistakes_frequency ON common_mistakes (frequency DESC);

INSERT INTO common_mistakes
    (chapitre_id, error_type, error_pattern, frequency, feedback_ar, feynman_prompt)
VALUES

-- Chapitre 4 : Immunité
('ch4_immunite', 'chiffres',
 'augment|زيادة|رفع|ارتفع(?!.*\\d)',
 0.72,
 'ذكرت زيادة لكن بدون أرقام. ما هي القيمة الدقيقة بالـ UA والأيام من الوثيقة؟',
 'اشرح لماذا يجب دائماً ذكر الأرقام الدقيقة في التحليل'),

('ch4_immunite', 'vocabulaire',
 'خلايا.*ذاكرة(?!.*LBm|.*LTm)',
 0.65,
 'انتبه! هناك نوعان: خلايا ذاكرة B (LBm) تنتج الأجسام المضادة، وخلايا ذاكرة T (LTm) للاستجابة الخلوية. أيهما تقصد هنا؟',
 'اشرح الفرق بين LBm و LTm كأنك تشرح لصديق لا يعرف علم الأحياء'),

('ch4_immunite', 'vocabulaire',
 'جسم مضاد(?!.*غلوبولين|.*immunoglobuline)',
 0.58,
 'الاسم العلمي الدقيق هو "الغلوبولين المناعي (Immunoglobuline)". استخدام الاسم الصحيح ضروري في الباكالوريا.',
 NULL),

-- Chapitre 1 : Synthèse des protéines
('ch1_proteines', 'vocabulaire',
 'انزيم(?!.*بوليميراز|.*ARN polymérase)',
 0.61,
 'أي إنزيم تقصد بالضبط؟ في الاستنساخ، الإنزيم المسؤول هو ARN بوليميراز (ARN Polymérase).',
 'اشرح دور ARN بوليميراز خطوة بخطوة كأنك تعلّم زميلك'),

('ch1_proteines', 'manhajia',
 '^(?!.*يتضح من الوثيقة|.*تبين الوثيقة|.*يظهر من)',
 0.69,
 'لم تبدأ بتحليل الوثيقة. يجب أن تبدأ بـ "تبين الوثيقة أن..." وتذكر القيم العددية أولاً قبل التفسير.',
 NULL),

('ch1_proteines', 'chiffres',
 'بسرعة|ببطء|بكمية(?!.*\\d)',
 0.55,
 'عبارة "بسرعة" غير مقبولة علمياً. استبدلها بالقيم الدقيقة من الوثيقة مع وحداتها.',
 NULL),

-- Chapitre 2 : Neurologie
('ch2_nerveux', 'vocabulaire',
 'رسالة عصبية(?!.*كمون عمل|.*potentiel d.action)',
 0.63,
 'الاسم الصحيح هو "كمون العمل (Potentiel d''action)". استخدم المصطلح الدقيق من الكتاب المدرسي.',
 'اشرح ما هو كمون العمل بكلماتك البسيطة'),

('ch2_nerveux', 'chiffres',
 'تغير في الجهد(?!.*mV|\\-70|\\-40|[+]\\d+)',
 0.71,
 'يجب ذكر القيم الدقيقة لجهد الراحة (-70mV) وجهد العمل (+30mV إلى +40mV).',
 NULL);
